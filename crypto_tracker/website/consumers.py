import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async
from django_celery_beat.models import PeriodicTask, IntervalSchedule

# class PriceConsumer(AsyncWebsocketConsumer):

#     @sync_to_async
#     def add_to_celery_beat(self, price):
#         task = PeriodicTask.objects.filter(name="every-10-seconds")
#         if len(task) > 0:
#             task = task.first()
#             args = json.loads(task.args)
#             args = args[0]
#             for x in price:
#                 if x not in args:
#                     args.append(x)
#             task.args = json.dumps([args])
#             task.save()
#         else:
#             schedule, created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)
#             task = PeriodicTask.objects.create(interval = schedule, name='every-10-seconds', task='website.tasks.update_price', args=json.dumps['price'])




#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = "price_%s" % self.room_name

#         # Join room group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)

#         #parse query_string
#         query_params = parse_qs(self.scope["query_string"].decode())
#         print(query_params)
#         price = query_params["price"]

#         #add to celery beat
#         await self.add_to_celery_beat(price)


#         await self.accept()
        


#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name, {"type": "price_update", "message": message}
#         )

#     # Receive message from room group
#     async def price_update(self, event):
#         message = event["message"]

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({"message": message}))