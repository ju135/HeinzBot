import grpc

import microservices.media_service.entpb_pb2 as entpb_pb2
import microservices.media_service.entpb_pb2_grpc as entpb_pb2_grpc


class MediaService:
    channel = None
    stub = None

    def __init__(self) -> None:
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = entpb_pb2_grpc.MediaServiceStub(self.channel)

    def create_media(self, message_id, chat_id, user_id, username, searchtext, command, type):
        try:
            media = entpb_pb2.Media()
            media.chat_id.value = str(chat_id)
            media.message_id.value = str(message_id)
            media.user_id.value = str(user_id)
            media.username.value = username
            media.searchtext.value = searchtext
            media.command.value = command
            media.type.value = type
            self.stub.Create(entpb_pb2.CreateMediaRequest(media=media))
        except Exception as e:
            print(e)
