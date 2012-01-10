
[rsync]: http://en.wikipedia.org/wiki/Rsync

### PyMachine: Apple's Time Machine for the rest of us

This Python script creates and maintains backups using the same ideas that makes Apple's Time Machine so efficient.

[Based on this blog](http://blog.interlinked.org/tutorials/rsync_time_machine.html).

Old backups are deleted:
	
- All backups within the last 24 hours are kept
- Only one backup is kept per day for the last 7 days
- Only one backup per week is kept for backups older than 3 months

This is great for remote backups, or when you want to have hourly backups on a USB stick yet consuming the minimum space.

### Usage

*Local:*

	pymachine.py ~/myFolderToBackup /Volumes/SomeUSBDrive/backups/myFolderToBackup

*Remote:*

	pymachine.py ~/myFolderToBackup loginName@myhost.com:/Volumes/SomeUSBDrive/backups/myFolderToBackup

### Requirements

*Local backups:*

- [rsync][Rsync]
- Python

*Remote backups:*

- Same as above, plus
- passwordless ssh
- Access to the /tmp folder on the remote machine