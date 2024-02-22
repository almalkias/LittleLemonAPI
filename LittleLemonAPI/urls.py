from django.urls import path
from . import views

urlpatterns = [
    # ================== Menu-Items Endpoints ===========================
    path('menu-items', views.menu_items),
    path('menu-items/<int:pk>', views.menu_item_detail),

#     # ============== User Group Management Endpoints =====================
    path('groups/manager/users', views.manage_manager_users),
    path('groups/manager/users/<int:pk>', views.unassign_manager),
    path('groups/delivery-crew/users', views.manage_delivery_crew_users),
    path('groups/delivery-crew/users/<int:pk>',
         views.unassign_delivery_crew),

#     # ================== Cart Management Endpoints ======================
    path('cart/menu-items', views.CartView.as_view()),

#     # ================== Order Management Endpoints =====================
    path('orders', views.OrdersView.as_view()),
    path('orders/<int:orderId>', views.OrderDetailView.as_view())
]