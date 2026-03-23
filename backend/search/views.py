from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .service import search_and_scrape
from .serializers import SearchResultSerializer


class SearchView(APIView):
    """
    POST /api/search/
    Body: { "query": "iPhone 15" }

    - Guests: scrapes live every time
    - Logged-in users: returns cached results instantly if searched
      within the last 30 minutes, otherwise scrapes fresh and caches
    """
    permission_classes = [AllowAny]

    def post(self, request):
        query = request.data.get("query", "").strip()

        if not query:
            return Response(
                {"error": "Search query is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(query) < 2:
            return Response(
                {"error": "Query too short. Please enter at least 2 characters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Pass user to service — it handles cache logic internally
        results = search_and_scrape(query, user=request.user)

        if not results:
            return Response(
                {"error": "No results found. Try a different search term."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Save to recently viewed if user is authenticated
        if request.user.is_authenticated:
            self._save_recently_viewed(request.user, results)

        serializer = SearchResultSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _save_recently_viewed(self, user, results):
        """Saves the top result to the user's recently viewed list."""
        try:
            from accounts.models import RecentlyViewed
            from products.models import Product

            if results:
                product = Product.objects.get(id=results[0]["id"])
                rv, created = RecentlyViewed.objects.update_or_create(
                    user=user,
                    product=product,
                )
                if not created:
                    rv.save()  # Force save to refresh viewed_at timestamp
        except Exception as e:
            print(f"[SearchView] Recently viewed save failed: {e}")


class ProductPriceView(APIView):
    """
    GET /api/search/product/<id>/

    Scrapes all 3 sites for the specific product and returns
    its prices across Amazon, Flipkart and Croma.
    Called by ProductPage.js when a user opens a product.
    """
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        from products.models import Product
        from .service import scrape_product_prices

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        result = scrape_product_prices(product)
        return Response(result, status=status.HTTP_200_OK)