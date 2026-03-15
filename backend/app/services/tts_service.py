import io
import asyncio
import json
import logging
import struct
import uuid
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Optional, List, Callable

import websockets

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class MsgType(IntEnum):
    """Message type enumeration"""
    Invalid = 0
    FullClientRequest = 0b1
    AudioOnlyClient = 0b10
    FullServerResponse = 0b1001
    AudioOnlyServer = 0b1011
    FrontEndResultServer = 0b1100
    Error = 0b1111
    ServerACK = AudioOnlyServer


class MsgTypeFlagBits(IntEnum):
    """Message type flag bits"""
    NoSeq = 0
    PositiveSeq = 0b1
    LastNoSeq = 0b10
    NegativeSeq = 0b11
    WithEvent = 0b100


class VersionBits(IntEnum):
    """Version bits"""
    Version1 = 1


class HeaderSizeBits(IntEnum):
    """Header size bits"""
    HeaderSize4 = 1


class SerializationBits(IntEnum):
    """Serialization method bits"""
    Raw = 0
    JSON = 0b1


class CompressionBits(IntEnum):
    """Compression method bits"""
    None_ = 0


@dataclass
class Message:
    """TTS message with proper protocol formatting"""
    version: VersionBits = VersionBits.Version1
    header_size: HeaderSizeBits = HeaderSizeBits.HeaderSize4
    type: MsgType = MsgType.Invalid
    flag: MsgTypeFlagBits = MsgTypeFlagBits.NoSeq
    serialization: SerializationBits = SerializationBits.JSON
    compression: CompressionBits = CompressionBits.None_
    sequence: int = 0
    error_code: int = 0
    payload: bytes = b""

    def marshal(self) -> bytes:
        """Serialize message to bytes"""
        buffer = io.BytesIO()
        
        # Write header (4 bytes)
        header = [
            (self.version << 4) | self.header_size,
            (self.type << 4) | self.flag,
            (self.serialization << 4) | self.compression,
            0  # Reserved
        ]
        buffer.write(bytes(header))
        
        # Write sequence if needed
        if self.flag in [MsgTypeFlagBits.PositiveSeq, MsgTypeFlagBits.NegativeSeq]:
            buffer.write(struct.pack(">i", self.sequence))
        elif self.type == MsgType.Error:
            buffer.write(struct.pack(">I", self.error_code))
        
        # Write payload with size prefix
        size = len(self.payload)
        buffer.write(struct.pack(">I", size))
        buffer.write(self.payload)
        
        return buffer.getvalue()

    @classmethod
    def from_bytes(cls, data: bytes) -> "Message":
        """Create message object from bytes"""
        if len(data) < 4:
            raise ValueError(f"Data too short: expected at least 4 bytes, got {len(data)}")
        
        buffer = io.BytesIO(data)
        
        # Read header
        version_and_header_size = buffer.read(1)[0]
        version = VersionBits(version_and_header_size >> 4)
        header_size = HeaderSizeBits(version_and_header_size & 0b00001111)
        
        type_and_flag = buffer.read(1)[0]
        msg_type = MsgType(type_and_flag >> 4)
        flag = MsgTypeFlagBits(type_and_flag & 0b00001111)
        
        serialization_compression = buffer.read(1)[0]
        serialization = SerializationBits(serialization_compression >> 4)
        compression = CompressionBits(serialization_compression & 0b00001111)
        
        # Skip reserved byte
        buffer.read(1)
        
        msg = cls(
            version=version,
            header_size=header_size,
            type=msg_type,
            flag=flag,
            serialization=serialization,
            compression=compression
        )
        
        # Read sequence if needed
        if flag in [MsgTypeFlagBits.PositiveSeq, MsgTypeFlagBits.NegativeSeq]:
            sequence_bytes = buffer.read(4)
            if sequence_bytes:
                msg.sequence = struct.unpack(">i", sequence_bytes)[0]
        elif msg_type == MsgType.Error:
            error_code_bytes = buffer.read(4)
            if error_code_bytes:
                msg.error_code = struct.unpack(">I", error_code_bytes)[0]
        
        # Read payload
        size_bytes = buffer.read(4)
        if size_bytes:
            size = struct.unpack(">I", size_bytes)[0]
            if size > 0:
                msg.payload = buffer.read(size)
        
        return msg

    def __str__(self) -> str:
        if self.type == MsgType.Error:
            return f"MsgType: {self.type}, ErrorCode: {self.error_code}, Payload: {self.payload.decode('utf-8', 'ignore')}"
        elif self.type in [MsgType.AudioOnlyServer, MsgType.AudioOnlyClient]:
            if self.flag in [MsgTypeFlagBits.PositiveSeq, MsgTypeFlagBits.NegativeSeq]:
                return f"MsgType: {self.type}, Sequence: {self.sequence}, PayloadSize: {len(self.payload)}"
            return f"MsgType: {self.type}, PayloadSize: {len(self.payload)}"
        else:
            if self.flag in [MsgTypeFlagBits.PositiveSeq, MsgTypeFlagBits.NegativeSeq]:
                return f"MsgType: {self.type}, Sequence: {self.sequence}, Payload: {self.payload.decode('utf-8', 'ignore')}"
            return f"MsgType: {self.type}, Payload: {self.payload.decode('utf-8', 'ignore')}"


class TTSService:
    """Service for interacting with Volcano TTS API using WebSocket"""
    
    def __init__(self):
        self.access_key = settings.volcano_access_key
        self.app_id = settings.volcano_app_id
        self.cluster = settings.volcano_cluster
        self.voice_type = settings.volcano_voice_type
        self.endpoint = "wss://openspeech.bytedance.com/api/v1/tts/ws_binary"
        # Create audio directory if it doesn't exist
        self.audio_dir = Path("backend/static/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cluster(self, voice: str) -> str:
        """Get cluster based on voice type"""
        if voice.startswith("S_"):
            return "volcano_icl"
        return self.cluster if self.cluster else "volcano_tts"
    
    async def generate_speech_async(self, text: str) -> dict:
        """
        Generate speech using Volcano TTS WebSocket API.
        
        Args:
            text: Text to convert to speech
        
        Returns:
            dict: {
                "audio_url": str (empty, as we save locally),
                "local_path": str (local file path)
            }
        """
        if not self.access_key or not self.app_id:
            raise Exception("Volcano TTS credentials not configured. Please set VOLCANO_ACCESS_KEY and VOLCANO_APP_ID in .env")
        
        cluster = self._get_cluster(self.voice_type)
        
        headers = {
            "Authorization": f"Bearer;{self.access_key}",
        }
        
        try:
            async with websockets.connect(
                self.endpoint,
                additional_headers=headers,
                max_size=10 * 1024 * 1024
            ) as websocket:
                # Prepare request payload
                request = {
                    "app": {
                        "appid": self.app_id,
                        "token": self.access_key,
                        "cluster": cluster,
                    },
                    "user": {
                        "uid": str(uuid.uuid4()),
                    },
                    "audio": {
                        "voice_type": self.voice_type,
                        "encoding": "mp3",
                    },
                    "request": {
                        "reqid": str(uuid.uuid4()),
                        "text": text,
                        "operation": "submit",
                        "with_timestamp": "1",
                        "extra_param": json.dumps({
                            "disable_markdown_filter": False,
                        }),
                    },
                }
                
                # Send request using proper Message format
                msg = Message(
                    type=MsgType.FullClientRequest,
                    flag=MsgTypeFlagBits.NoSeq,
                    serialization=SerializationBits.JSON
                )
                msg.payload = json.dumps(request).encode()
                await websocket.send(msg.marshal())
                logger.info(f"Sent TTS request for text: {text[:50]}...")
                
                # Receive audio data
                audio_data = bytearray()
                while True:
                    data = await websocket.recv()
                    if isinstance(data, bytes):
                        response_msg = Message.from_bytes(data)
                        logger.info(f"Received: {response_msg}")
                        
                        if response_msg.type == MsgType.FrontEndResultServer:
                            continue
                        elif response_msg.type == MsgType.AudioOnlyServer:
                            audio_data.extend(response_msg.payload)
                            if response_msg.sequence < 0:  # Last message
                                break
                        elif response_msg.type == MsgType.Error:
                            error_msg = response_msg.payload.decode('utf-8', errors='ignore')
                            raise Exception(f"TTS error (code {response_msg.error_code}): {error_msg}")
                        else:
                            logger.warning(f"Unexpected message type: {response_msg.type}")
                    else:
                        logger.warning(f"Unexpected data type: {type(data)}")
                
                if not audio_data:
                    raise Exception("No audio data received from TTS service")
                
                # Save to local file
                filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
                filepath = self.audio_dir / filename
                
                with open(filepath, "wb") as f:
                    f.write(audio_data)
                
                logger.info(f"Audio saved: {len(audio_data)} bytes to {filepath}")
                
                return {
                    "audio_url": "",
                    "local_path": f"/static/audio/{filename}"
                }
                
        except websockets.exceptions.WebSocketException as e:
            logger.error(f"WebSocket error: {str(e)}")
            raise Exception(f"WebSocket error: {str(e)}")
        except Exception as e:
            logger.error(f"TTS generation failed: {str(e)}")
            raise Exception(f"TTS generation failed: {str(e)}")
    
    def generate_speech(self, text: str) -> dict:
        """
        Synchronous wrapper for generate_speech_async.
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If we're already in an async context, create a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.generate_speech_async(text))
                return future.result()
        else:
            return loop.run_until_complete(self.generate_speech_async(text))
    
    def get_audio_path(self, relative_path: str) -> Optional[str]:
        """Get absolute path for a relative audio path"""
        if relative_path:
            # Remove /static/ prefix if present
            clean_path = relative_path.replace("/static/", "")
            full_path = Path("backend/static") / clean_path
            if full_path.exists():
                return str(full_path)
        return None


# Create a singleton instance
tts_service = TTSService()
