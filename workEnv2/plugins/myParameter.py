from platform import system
# print(f"System: {system()}")
if system() == "Windows":
    ubot1output = "../output.txt"
    ubot2output = "../output.txt"
    infobotoutput = "../../infobot/output.txt"
elif system() == "Linux":
    ubot1output = "/home/ubuntu/Magnus/PycharmProj/ubot/output.txt"
    ubot2output = "/home/ubuntu/Magnus/PycharmProj/ubot2/output.txt"
    infobotoutput = "/home/ubuntu/Magnus/PycharmProj/infobot/output.txt"
my_id = 1259233812
# terminal_id = -4030133781
terminal_id = -1001995530063  # update to supergroup
# Forum: Saved Message > Topic:Pic
saved_message_forum_id = -1001971247646
pic_topic_id = 18
