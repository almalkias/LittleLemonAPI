from rest_framework import serializers
from .models import Cart, MenuItem, Order, OrderItem


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
        

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']
        read_only_fields = ['unit_price', 'price']

    def create(self, validated_data):
        validated_data['unit_price'] = validated_data['menuitem'].price
        validated_data['price'] = validated_data[
            'menuitem'].price * validated_data['quantity']
        return super().create(validated_data)

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'delivery_crew', 'total', 'date', 'order_items'
        ]
        read_only_fields = [
            'total', 'date', 'order_items', 'user'
        ] 

    def create(self, validated_data):
        user = self.context['request'].user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            raise serializers.ValidationError("The cart is empty.")

        order = Order.objects.create(user=user, total=0) 
        total_price = sum([item.quantity * item.menuitem.price for item in cart_items])

        # Create OrderItems from CartItems
        for item in cart_items:
            OrderItem.objects.create(order=order,
                                     menuitem=item.menuitem,
                                     quantity=item.quantity,
                                     unit_price=item.menuitem.price,
                                     price=item.quantity * item.menuitem.price)

        # Update the total price of the order after all items have been added
        order.total = total_price
        order.save()

        # Clear the cart
        cart_items.delete()

        return order