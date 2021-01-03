import android
from jnius import autoclass

ANDROID_VERSION = autoclass('android.os.Build$VERSION')
SDK_INT = ANDROID_VERSION.SDK_INT

Service = autoclass('org.kivy.android.PythonService').mService
notifi = autoclass("android.app.Notification$Builder")(Service)
notifi.setContentTitle("ZeroNet")
notifi.setContentText("ZeroNet is running")

if SDK_INT >= 26:
    manager = autoclass('android.app.NotificationManager') # manager is NotificationManager
    channel = autoclass('android.app.NotificationChannel')
    managerID = autoclass('android.content.Context').NOTIFICATION_SERVICE

    app_channel = channel( # val mChannel = NotificationChannel(CHANNEL_ID, name, importance)
        "service_zn", "ZeroNet Background Service", manager.IMPORTANCE_MIN # val importance = NotificationManager.IMPORTANCE_DEFAULT
    )
    Service.getSystemService(managerID).createNotificationChannel(app_channel) # val notificationManager = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
    # notificationManager.createNotificationChannel(mChannel)
    notifi.setChannel("service_zn")
#    if SDK_INT >= 28:
#        Service.startForeground(233,notifi)
#    else:
#        notification = notifi.build()
#        Service.startForeground(233,notification)
notification = notifi.build()
Service.startForeground(233,notification)