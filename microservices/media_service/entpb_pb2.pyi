from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateMediaRequest(_message.Message):
    __slots__ = ["media"]
    MEDIA_FIELD_NUMBER: _ClassVar[int]
    media: Media
    def __init__(self, media: _Optional[_Union[Media, _Mapping]] = ...) -> None: ...

class DeleteMediaRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetMediaRequest(_message.Message):
    __slots__ = ["id", "view"]
    class View(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    BASIC: GetMediaRequest.View
    ID_FIELD_NUMBER: _ClassVar[int]
    VIEW_FIELD_NUMBER: _ClassVar[int]
    VIEW_UNSPECIFIED: GetMediaRequest.View
    WITH_EDGE_IDS: GetMediaRequest.View
    id: int
    view: GetMediaRequest.View
    def __init__(self, id: _Optional[int] = ..., view: _Optional[_Union[GetMediaRequest.View, str]] = ...) -> None: ...

class ListMediaRequest(_message.Message):
    __slots__ = ["page_size", "page_token", "view"]
    class View(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    BASIC: ListMediaRequest.View
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    VIEW_FIELD_NUMBER: _ClassVar[int]
    VIEW_UNSPECIFIED: ListMediaRequest.View
    WITH_EDGE_IDS: ListMediaRequest.View
    page_size: int
    page_token: str
    view: ListMediaRequest.View
    def __init__(self, page_size: _Optional[int] = ..., page_token: _Optional[str] = ..., view: _Optional[_Union[ListMediaRequest.View, str]] = ...) -> None: ...

class ListMediaResponse(_message.Message):
    __slots__ = ["media_list", "next_page_token"]
    MEDIA_LIST_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    media_list: _containers.RepeatedCompositeFieldContainer[Media]
    next_page_token: str
    def __init__(self, media_list: _Optional[_Iterable[_Union[Media, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...

class Media(_message.Message):
    __slots__ = ["chat_id", "command", "created_at", "deleted_at", "id", "message_id", "searchtext", "type", "user_id", "username"]
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    DELETED_AT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCHTEXT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    chat_id: _wrappers_pb2.StringValue
    command: _wrappers_pb2.StringValue
    created_at: _timestamp_pb2.Timestamp
    deleted_at: _timestamp_pb2.Timestamp
    id: int
    message_id: _wrappers_pb2.StringValue
    searchtext: _wrappers_pb2.StringValue
    type: _wrappers_pb2.StringValue
    user_id: _wrappers_pb2.StringValue
    username: _wrappers_pb2.StringValue
    def __init__(self, id: _Optional[int] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., deleted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., chat_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., username: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., user_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., message_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., type: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., command: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., searchtext: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...
