from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int
    key: str
    role: str
    password: str
    creation: datetime
    deleted: bool


@dataclass
class Session:
    id: int
    token_hash: str
    user_id: int
    creation: datetime
    expiration: datetime
    deleted: bool


@dataclass
class Student:
    id: int
    name: str
    icon: memoryview
    icon_media_type: str


@dataclass
class Administrative:
    id: int
    name: str
    acronym: str
    type: str
    country: str
    website: str
    icon: memoryview
    icon_media_type: str


@dataclass
class AdministrativeMessage:
    id: int
    subject: str
    body: str
    creation: datetime
    sender_id: int
    recipient_id: int
    deleted: bool


@dataclass
class AdministrativeMessageFile:
    id: int
    name: str
    media_type: str
    content: memoryview
    administrative_message_id: int


@dataclass
class CallFor:
    id: int
    title: str
    initial_date: datetime | None
    final_date: datetime | None
    description: str
    requirements: str
    destination_country: str
    publish_date: datetime
    modification: datetime
    administrative_id: int
    deleted: bool


@dataclass
class FrequentQuestion:
    id: int
    question: str
    answer: str
    call_for_id: int
    deleted: bool


@dataclass
class Link:
    id: int
    title: str
    url: str
    call_for_id: int
    deleted: bool


@dataclass
class ForumFile:
    id: int
    title: str
    name: str
    media_type: str
    content: memoryview
    modification: datetime
    call_for_id: int
    deleted: bool


@dataclass
class ForumMessage:
    id: int
    content: str
    creation: datetime
    attached_image: memoryview
    image_media_type: str
    user_id: int
    call_for_id: int
    deleted: bool


@dataclass
class FileRequest:
    id: int
    title: str
    call_for_id: int
    deleted: bool


@dataclass
class Application:
    id: int
    student_id: int
    call_for_id: int
    deleted: bool


@dataclass
class StudentFile:
    application_id: int
    file_request_id: int
    name: str
    media_type: str
    content: memoryview
    modification: datetime
    deleted: bool


@dataclass
class PrivateMessage:
    id: int
    content: str
    creation: datetime
    attached_image: memoryview
    image_media_type: str
    user_id: int
    application_id: int
    deleted: bool