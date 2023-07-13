text_sync = "Sync this. #sync"
text_nosync = "Do not sync this."

text = text_sync

if text.find('#sync') != -1:
    print('Synced!')
else:
    print('Not synced')

