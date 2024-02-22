from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView


def is_manager(user):
    return user.groups.filter(name='Manager').exists()

def is_delivery_crew(user):
    return user.groups.filter(name='Delivery crew').exists()


# def get_group_and_user(group_name, user_id):
#     group = get_object_or_404(Group, name=group_name)
#     user = get_object_or_404(User, pk=user_id)
#     return group, user


# ================== Menu-Items Endpoints ===========================
@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.all()
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if is_manager(request.user):
            serializer = MenuItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Unauthorized"},
                            status=status.HTTP_403_FORBIDDEN)

    elif request.method in ['PUT', 'PATCH', 'DELETE']:
        return Response({"detail": "Unauthorized"},
                        status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_item_detail(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)

    if request.method == 'GET':
        serializer = MenuItemSerializer(item)
        return Response(serializer.data)

    if is_manager(request.user):
        if request.method in ['PUT', 'PATCH']:
            serializer = MenuItemSerializer(
                item, data=request.data, partial=(request.method == 'PATCH'))
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            item.delete()
            return Response({"detail": "Item deleted successfully."},
                            status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Unauthorized"},
                        status=status.HTTP_403_FORBIDDEN)


# ============== User Group Management Endpoints =====================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_manager_users(request):
    if not is_manager(request.user):
        return Response(
            {
                "detail":
                "Unauthorized - Only managers can access this endpoint."
            },
            status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        manager_group = Group.objects.get(name='Manager')
        managers = manager_group.user_set.all()
        manager_usernames = [user.username for user in managers]
        return Response(manager_usernames)

    elif request.method == 'POST':
        username = request.data.get('username')
        try:
            user_to_add = User.objects.get(username=username)
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.add(user_to_add)
            return Response(
                {
                    "detail":
                    f"User {user_to_add.username} added to Manager group."
                },
                status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"detail": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unassign_manager(request, pk):
    if not is_manager(request.user):
        return Response(
            {
                "detail":
                "Unauthorized - Only managers can access this endpoint."
            },
            status=status.HTTP_403_FORBIDDEN)

    user = get_object_or_404(User, pk=pk)

    manager_group = Group.objects.get(name='Manager')
    manager_group.user_set.remove(user)
    return Response(
        {"detail": f"User {user.username} removed from Manager group."},
        status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_delivery_crew_users(request):
    if not is_manager(request.user):
        return Response(
            {
                "detail":
                "Unauthorized - Only managers can access this endpoint."
            },
            status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        delivery_crew_group = Group.objects.get(name='Delivery crew')
        delivery_crew_users = delivery_crew_group.user_set.all()
        delivery_crew_users_list = [user.username for user in delivery_crew_users]
        return Response(delivery_crew_users_list)

    elif request.method == 'POST':
        username = request.data.get('username')
        try:
            user_to_add = User.objects.get(username=username)
            delivery_crew_group = Group.objects.get(name='Delivery crew')
            delivery_crew_group.user_set.add(user_to_add)
            return Response(
                {
                    "detail":
                    f"User {user_to_add.username} added to Delivery crew group."
                },
                status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"detail": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unassign_delivery_crew(request, pk):
    if not is_manager(request.user):
        return Response(
            {
                "detail":
                "Unauthorized - Only managers can access this endpoint."
            },
            status=status.HTTP_403_FORBIDDEN)

    user = get_object_or_404(User, pk=pk)

    delivery_crew_group = Group.objects.get(name='Delivery crew')
    delivery_crew_group.user_set.remove(user)
    return Response(
        {"detail": f"User {user.username} removed from Delivery crew group."},
        status=status.HTTP_200_OK)


# # ============== Cart Management Endpoints =====================
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        carts = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CartSerializer(data=request.data,
                                    context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# # ============== Order Management Endpoints =====================
class OrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if is_manager(request.user):
            orders = Order.objects.all()
        elif is_delivery_crew(request.user):
            orders = Order.objects.filter(delivery_crew=request.user)
        else:
            orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            return Response(
                {
                    "detail": "Order created successfully.",
                    "order_id": order.id
                },
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, orderId):
        order = get_object_or_404(Order, id=orderId)
        if order.user != request.user:
            return Response({"detail": "Not authorized to view this order."},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, orderId):
        if not is_manager(request.user):
            return Response({"detail": "Only managers can update orders."},
                            status=status.HTTP_403_FORBIDDEN)
        order = self.get_object(orderId)
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, orderId):
        order = self.get_object(orderId)
        if not is_manager(request.user) and order.delivery_crew != request.user:
            return Response({"detail": "Not authorized to update this order."},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, orderId):
        if not is_manager(request.user):
            return Response({"detail": "Only managers can delete orders."},
                            status=status.HTTP_403_FORBIDDEN)
        order = get_object_or_404(Order, id=orderId)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
