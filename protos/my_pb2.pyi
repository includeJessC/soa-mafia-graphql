from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CheckPlayerRequest(_message.Message):
    __slots__ = ["id", "session"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    id: int
    session: str
    def __init__(self, session: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class ConnectedPlayers(_message.Message):
    __slots__ = ["id", "names"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAMES_FIELD_NUMBER: _ClassVar[int]
    id: int
    names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[int] = ..., names: _Optional[_Iterable[str]] = ...) -> None: ...

class ConnectedPlayersOnly(_message.Message):
    __slots__ = ["names"]
    NAMES_FIELD_NUMBER: _ClassVar[int]
    names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, names: _Optional[_Iterable[str]] = ...) -> None: ...

class DisconnectRequest(_message.Message):
    __slots__ = ["id", "session"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    id: int
    session: str
    def __init__(self, session: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class EndDayRequest(_message.Message):
    __slots__ = ["id", "session"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    id: int
    session: str
    def __init__(self, session: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class EndDayResponse(_message.Message):
    __slots__ = ["end_game", "killed"]
    END_GAME_FIELD_NUMBER: _ClassVar[int]
    KILLED_FIELD_NUMBER: _ClassVar[int]
    end_game: bool
    killed: int
    def __init__(self, killed: _Optional[int] = ..., end_game: bool = ...) -> None: ...

class EndNightResponse(_message.Message):
    __slots__ = ["checked", "checked_role", "end_game", "killed"]
    CHECKED_FIELD_NUMBER: _ClassVar[int]
    CHECKED_ROLE_FIELD_NUMBER: _ClassVar[int]
    END_GAME_FIELD_NUMBER: _ClassVar[int]
    KILLED_FIELD_NUMBER: _ClassVar[int]
    checked: int
    checked_role: str
    end_game: bool
    killed: int
    def __init__(self, checked_role: _Optional[str] = ..., end_game: bool = ..., killed: _Optional[int] = ..., checked: _Optional[int] = ...) -> None: ...

class KillPlayerMafiaRequest(_message.Message):
    __slots__ = ["id", "session"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    id: int
    session: str
    def __init__(self, session: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class KillVoteRequest(_message.Message):
    __slots__ = ["id", "session"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    id: int
    session: str
    def __init__(self, session: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class NotificationsRequest(_message.Message):
    __slots__ = ["id", "session"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    id: int
    session: str
    def __init__(self, session: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class NotificationsResponse(_message.Message):
    __slots__ = ["connected", "user_name"]
    CONNECTED_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    connected: bool
    user_name: str
    def __init__(self, connected: bool = ..., user_name: _Optional[str] = ...) -> None: ...

class Player(_message.Message):
    __slots__ = ["id", "name", "role"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    role: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., role: _Optional[str] = ...) -> None: ...

class ReadyRequest(_message.Message):
    __slots__ = ["id", "session"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    id: int
    session: str
    def __init__(self, session: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class ReadyResponse(_message.Message):
    __slots__ = ["ids", "players", "role"]
    IDS_FIELD_NUMBER: _ClassVar[int]
    PLAYERS_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedScalarFieldContainer[int]
    players: _containers.RepeatedScalarFieldContainer[str]
    role: str
    def __init__(self, role: _Optional[str] = ..., players: _Optional[_Iterable[str]] = ..., ids: _Optional[_Iterable[int]] = ...) -> None: ...

class ScoreBoard(_message.Message):
    __slots__ = ["is_ended", "is_mafia_win", "players"]
    IS_ENDED_FIELD_NUMBER: _ClassVar[int]
    IS_MAFIA_WIN_FIELD_NUMBER: _ClassVar[int]
    PLAYERS_FIELD_NUMBER: _ClassVar[int]
    is_ended: bool
    is_mafia_win: bool
    players: _containers.RepeatedCompositeFieldContainer[Player]
    def __init__(self, is_mafia_win: bool = ..., is_ended: bool = ..., players: _Optional[_Iterable[_Union[Player, _Mapping]]] = ...) -> None: ...

class SessionName(_message.Message):
    __slots__ = ["session"]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    session: str
    def __init__(self, session: _Optional[str] = ...) -> None: ...

class SessionsName(_message.Message):
    __slots__ = ["sessions"]
    SESSIONS_FIELD_NUMBER: _ClassVar[int]
    sessions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, sessions: _Optional[_Iterable[str]] = ...) -> None: ...

class SetUserNameRequest(_message.Message):
    __slots__ = ["name", "session"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    name: str
    session: str
    def __init__(self, session: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class SkipNightRequest(_message.Message):
    __slots__ = ["session"]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    session: str
    def __init__(self, session: _Optional[str] = ...) -> None: ...
