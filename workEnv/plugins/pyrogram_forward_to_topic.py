"""
funzione esterna non presente in pyrogram
"""
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.raw import functions, types


async def forward_to_topic(
        source_channel_id: int, destination_channel_id: int,
        forwarded_message_id: int, topic_init_message_id: int, client: Client) -> Message:
    """
    Forward a message from one channel to another channel and associate it with a specified topic using raw functions,
    while topic support is not provided by pyrogram. Uses top_msg_id, which can be found in url of the topic as last
    element. For example, in https://t.me/teriberka/22 - 22 is top message id of topic. Can be found in message object
    as a 'reply_to_top_message_id'.
    Args:
        source_channel_id (int): The ID of the source channel from where the message should be forwarded.
        destination_channel_id (int): The ID of the destination channel where the message should be forwarded.
        forwarded_message_id (int): The message ID of the message that should be forwarded.
        topic_init_message_id (int): The message ID of the message that represents the start of the topic
                                     in the destination channel.
        client (Client): The Pyrogram client object used to make the API calls.
    Returns:
        Union[Message, types.MessagesAffectedMessages]: The forwarded message object if the operation was successful,
                                                         otherwise the messages affected by the operation.
    """
    if not isinstance(source_channel_id, int) or not isinstance(destination_channel_id, int):
        raise TypeError("The channel IDs must be integers.")
    if not isinstance(forwarded_message_id, int) or not isinstance(topic_init_message_id, int):
        raise TypeError("The message IDs must be integers.")

    # Represent channel ids for raw usage according to https://docs.pyrogram.org/topics/advanced-usage

    repr_source_channel_id = int(str(source_channel_id)[4:])
    repr_destination_channel_id = int(str(destination_channel_id)[4:])

    # Get access hashes for the channels

    source_channel_full = await client.invoke(
        functions.channels.GetFullChannel(
            channel=await client.resolve_peer(source_channel_id)
        )
    )

    destination_channel_full = await client.invoke(
        functions.channels.GetFullChannel(
            channel=await client.resolve_peer(destination_channel_id)
        )
    )

    # Forward raw

    forwarded_message = await client.invoke(
        functions.messages.ForwardMessages(
            from_peer=types.InputPeerChannel(
                channel_id=repr_source_channel_id,
                access_hash=source_channel_full.chats[0].access_hash
            ),
            random_id=[client.rnd_id()],
            id=[forwarded_message_id],
            top_msg_id=topic_init_message_id,
            to_peer=types.InputPeerChannel(
                channel_id=repr_destination_channel_id,
                access_hash=destination_channel_full.chats[0].access_hash
            )
        )
    )

    return forwarded_message
