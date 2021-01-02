import jnius
Context = jnius.autoclass('android.content.Context')
Intent = jnius.autoclass('android.content.Intent')
PendingIntent = jnius.autoclass('android.app.PendingIntent')
AndroidString = jnius.autoclass('java.lang.String')
NotificationBuilder = jnius.autoclass('android.app.Notification$Builder')
Notification = jnius.autoclass('android.app.Notification')
service_name = 'S1'
package_name = 'com.something'
service = jnius.autoclass('org.kivy.android.PythonService').mService
# Previous version of Kivy had a reference to the service like below.
#service = jnius.autoclass('{}.Service{}'.format(package_name, service_name)).mService
PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
notification_service = service.getSystemService(
    Context.NOTIFICATION_SERVICE)
app_context = service.getApplication().getApplicationContext()
notification_builder = NotificationBuilder(app_context)
title = AndroidString("Black Hole".encode('utf-8'))
message = AndroidString("Ready to play music".encode('utf-8'))
app_class = service.getApplication().getClass()
notification_intent = Intent(app_context, PythonActivity)
notification_intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP |
    Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_NEW_TASK)
notification_intent.setAction(Intent.ACTION_MAIN)
notification_intent.addCategory(Intent.CATEGORY_LAUNCHER)
intent = PendingIntent.getActivity(service, 0, notification_intent, 0)
notification_builder.setContentTitle(title)
notification_builder.setContentText(message)
notification_builder.setContentIntent(intent)
Drawable = jnius.autoclass("{}.R$drawable".format(service.getPackageName()))
icon = getattr(Drawable, 'icon')
notification_builder.setSmallIcon(icon)
notification_builder.setAutoCancel(True)
new_notification = notification_builder.getNotification()
#Below sends the notification to the notification bar; nice but not a foreground service.
#notification_service.notify(0, new_noti)
service.startForeground(1, new_notification)