
from rest_app.serializers import *
from rest_app.models import *
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Case, When
from .models import *



# register **
class Register(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        mutable = request.POST._mutable
        request.POST._mutable = True
        request.POST['username'] = request.POST['email']
        request.POST._mutable = mutable
        serializer = UserSerializer(data=request.data)
        validate = serializer.is_valid()
        if validate is False:
            return Response({"status": 400, "message": "Incorrect Inputs", "data": serializer.errors})

        user = User.objects.create_user(name=request.POST['name'], phone_number=request.POST['phone_number'], username=request.POST['email'],
                                        email=request.POST['email'], password=request.POST['password'])
        user.is_active = True
        user.is_gmail_authenticated = True
        user.save()

        fields = ('id', 'username', 'email', 'phone_number', 'name')
        data = UserSerializer(user, many=False, fields=fields)
        response = {
            'success': 'True',
            'status': 200,
            'message': 'User created successfully',
            'data': data.data,
        }

        return Response(response)


# login **
class UserLogin(APIView):
    permission_classes = [AllowAny]

    class Validation(serializers.Serializer):
        email = serializers.CharField()
        password = serializers.CharField()

    def post(self, request):

        validation = self.Validation(data=request.data)
        validate = validation.is_valid()
        if validate is False:
            return Response({"status": 400, "message": "Incorrect Inputs", "data": validation.errors})

        user = User.objects.filter(
            email=request.POST['email'], is_gmail_authenticated=True).first()

        if user:
            mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['password'] = request.POST['password']
            request.POST._mutable = mutable
            serializer = UserLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            fields = ('id', 'username', 'email', 'phone_number', 'name')
            data = UserSerializer(user, many=False, fields=fields)
            response = {
                'success': 'True',
                'status': 200,
                'message': 'User logged in successfully',
                'token': serializer.data['token'],
                'data': data.data,
            }

            return Response(response)



# registration and auto login **
class RegisterandLogin(APIView):
    permission_classes = [AllowAny]

    class Validation(serializers.Serializer):
        email = serializers.CharField()
        name = serializers.CharField()

    def post(self, request):

        validation = self.Validation(data=request.data)
        validate = validation.is_valid()
        if validate is False:
            return Response({"status": 400, "message": "Incorrect Inputs", "data": validation.errors})

        user = User.objects.filter(
            email=request.POST['email'], is_gmail_authenticated=True).first()

        if user:
            mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['password'] = 'captainamerica'
            request.POST._mutable = mutable
            serializer = UserLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            fields = ('id', 'username', 'email', 'phone_number', 'name')
            data = UserSerializer(user, many=False, fields=fields)
            response = {
                'success': 'True',
                'status': 200,
                'message': 'User logged in  successfully',
                'token': serializer.data['token'],
                'data': data.data,
            }

            return Response(response)
        else:
            mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['password'] = 'captainamerica'
            request.POST['username'] = request.POST['email']
            request.POST._mutable = mutable
            serializer = UserSerializer(data=request.data)
            validate = serializer.is_valid()
            if validate is False:
                return Response({"status": 400, "message": "Incorrect Inputs", "data": serializer.errors})

            user = User.objects.create_user(name=request.POST['name'], username=request.POST['email'],
                                            email=request.POST['email'], password='captainamerica')
            user.is_active = True
            user.is_gmail_authenticated = True
            user.save()

            serializer = UserLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            fields = ('id', 'username', 'email', 'phone_number', 'name')
            data = UserSerializer(user, many=False, fields=fields)
            response = {
                'success': 'True',
                'status': 200,
                'message': 'User created and logged in  successfully',
                'token': serializer.data['token'],
                'data': data.data,
            }

            return Response(response)



# authenticated_userr **
class UserDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = User.objects.filter(id=request.user.id)
        serializer = UserSerializer(items, many=True)
        return Response({'data':serializer.data,'status': 200, "message": "success"})


class BookingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        venue_id = request.data.get('venue_id')
        date = request.data.get('date')
        time_slot = request.data.get('time_slot')
        existing_booking = Booking.objects.filter(
            venue_id=venue_id, date=date, time_slot=time_slot).first()
        if existing_booking is not None:
            return Response({'message': 'Time slot not available'}, status=status.HTTP_400_BAD_REQUEST)
        booking = Booking(user_id=user_id, venue_id=venue_id, date=date, time_slot=time_slot)
        booking.save()
        return Response({'message': 'Booking successful'})

    

class VenueView(APIView):
    permission_classes = [IsAuthenticated]
  
    def get(self, request):
        venues = Venue.objects.annotate(
            booking_count=Count(Case(When(booking__date__month=4, then=1))))
        data = []
        for venue in venues:
            category = 'Other'
            if venue.booking_count > 15:
                category = 'Gold'
            elif venue.booking_count >= 10:
                category = 'Silver'
            elif venue.booking_count >= 5:
                category = 'Bronze'
            data.append({
                'venue_id': venue.id,
                'venue_name': venue.name,
                'category': category,
                'booking_count': venue.booking_count
            })
        return Response({'venues': data})