from rest_framework.views import APIView


class OrderListCreateView(APIView):
    """API view for listing and creating orders."""

    pass


class OrderDetailView(APIView):
    """API view for updating and deleting a specific order."""

    pass


class OrderCountView(APIView):
    """API view for counting the total business user orders."""

    pass


class CompletedOrderCountView(APIView):
    """API view for counting the completed business user orders."""

    pass