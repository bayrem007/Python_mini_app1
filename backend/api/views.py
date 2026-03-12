from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from data_loader.services import OpenFoodFactsService
from products.models import Product
from products.serializers import ProductSerializer
from products.services import get_product_by_barcode, get_product_by_id, search_products
from substitutions.models import Substitution
from substitutions.serializers import SubstitutionResultSerializer
from substitutions.services import SubstitutionService, save_substitution
from users.serializers import (
    LoginSerializer,
    ProfileSerializer,
    RegisterSerializer,
)
from api.serializers import (
    SubstitutionFindRequestSerializer,
    SubstitutionSaveRequestSerializer,
)


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok"})


class ProductSearchView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "")
        limit = int(request.query_params.get("limit", "20"))
        products = search_products(q, limit=limit)
        return Response([ProductSerializer.from_document(p) for p in products])


class ProductDetailView(APIView):
    def get(self, request, product_id: str):
        product = get_product_by_id(product_id)
        if not product:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProductSerializer.from_document(product))


class SubstitutionListView(APIView):
    def get(self, request):
        product_id = request.query_params.get("product_id", "")
        limit = int(request.query_params.get("limit", "10"))
        service = SubstitutionService()
        result = service.find_substitute(product_id)
        if not result:
            return Response({"detail": "Product not found or no substitute available"}, status=status.HTTP_404_NOT_FOUND)
        return Response(result)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)


class CategoryListView(APIView):
    """
    GET /api/categories
    Returns distinct product categories.
    """

    def get(self, request):
        categories = (
            Product.objects(category__ne=None)
            .distinct("category")
        )
        categories = [c for c in categories if c]
        return Response({"categories": categories})


class ProductsByCategoryView(APIView):
    """
    GET /api/products?category=...
    """

    def get(self, request):
        category = (request.query_params.get("category") or "").strip()
        if not category:
            return Response(
                {"detail": "category query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = Product.objects(category=category).order_by("name")[:100]
        data = [ProductSerializer.from_document(p) for p in qs]
        return Response(data)


class ProductByBarcodeView(APIView):
    """
    GET /api/products/barcode/{barcode}
    """

    def get(self, request, barcode: str):
        product = get_product_by_barcode(barcode)
        if not product:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProductSerializer.from_document(product))


class ProductFetchByBarcodeView(APIView):
    """
    GET /api/products/barcode/{barcode}/fetch/
    Fetches a product from OpenFoodFacts API by barcode and saves it to database.
    """

    def get(self, request, barcode: str):
        service = OpenFoodFactsService()
        product = service.fetch_and_save_product_by_barcode(barcode)
        if not product:
            return Response({"detail": "Product not found or not available for French market"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProductSerializer.from_document(product))


class ProductTestByBarcodeView(APIView):
    """
    GET /api/products/barcode/{barcode}/test/
    Tests fetching a product from OpenFoodFacts API by barcode without saving to database.
    """

    def get(self, request, barcode: str):
        service = OpenFoodFactsService()
        product = service.fetch_product_by_barcode(barcode)
        if not product:
            return Response({"detail": "Product not found or not available for French market"}, status=status.HTTP_404_NOT_FOUND)
        
        # Return basic product info
        return Response({
            "barcode": product.get("code"),
            "name": product.get("product_name"),
            "brand": product.get("brands"),
            "nutriscore": product.get("nutriscore_grade"),
            "categories": product.get("categories"),
            "countries": product.get("countries"),
            "is_french": service._is_french_product(product)
        })


class ProductSearchByNameView(APIView):
    """
    GET /api/products/name/{search_terms}/
    Search for products by name using OpenFoodFacts API.
    """

    def get(self, request, search_terms: str):
        service = OpenFoodFactsService()
        products = service.search_products_by_name(search_terms)
        
        if not products:
            return Response({"detail": "No products found", "products": []}, status=status.HTTP_404_NOT_FOUND)
        
        # Return basic product info for each product
        result_products = []
        for product in products:
            result_products.append({
                "barcode": product.get("code"),
                "name": product.get("product_name"),
                "brand": product.get("brands"),
                "nutriscore": product.get("nutriscore_grade"),
                "categories": product.get("categories"),
                "countries": product.get("countries"),
                "is_french": service._is_french_product(product),
                "image_url": product.get("image_url")
            })
        
        return Response({
            "search_terms": search_terms,
            "count": len(result_products),
            "products": result_products
        })


class SubstitutionFindView(APIView):
    """
    POST /api/substitutions/find
    Body: { "product_id": "<id>" }
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SubstitutionFindRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data["product_id"]
        service = SubstitutionService()
        result = service.find_substitute(product_id)
        if result is None:
            return Response(
                {"detail": "No suitable substitute found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(result, status=status.HTTP_200_OK)


class SubstitutionSaveView(APIView):
    """
    POST /api/substitutions/save
    Body: { "product_id": "<id>", "substitute_id": "<id>" }
    Requires authentication.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SubstitutionSaveRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data["product_id"]
        substitute_id = serializer.validated_data["substitute_id"]

        original = Product.objects(id=product_id).first()
        substitute = Product.objects(id=substitute_id).first()
        if not original or not substitute:
            return Response(
                {"detail": "Product or substitute not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            saved = save_substitution(str(request.user.id), original, substitute)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "id": str(saved.id),
                "original_product_id": str(saved.original_product.id),
                "substitute_product_id": str(saved.substitute_product.id),
            },
            status=status.HTTP_201_CREATED,
        )


class MySubstitutionsView(APIView):
    """
    GET /api/substitutions/my
    Returns the current user's saved substitutions.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id = str(request.user.id)
        subs = Substitution.objects(user__id=user_id)

        results = []
        for s in subs:
            orig = s.original_product
            sub = s.substitute_product
            results.append(
                {
                    "id": str(s.id),
                    "original": {
                        "id": str(orig.id),
                        "name": orig.name,
                        "brand": orig.brand,
                        "barcode": orig.barcode,
                        "nutriscore": orig.nutriscore,
                        "category": orig.category,
                        "image_url": orig.image_url,
                        "openfoodfacts_url": orig.openfoodfacts_url,
                    },
                    "substitute": {
                        "id": str(sub.id),
                        "name": sub.name,
                        "brand": sub.brand,
                        "barcode": sub.barcode,
                        "nutriscore": sub.nutriscore,
                        "category": sub.category,
                        "image_url": sub.image_url,
                        "openfoodfacts_url": sub.openfoodfacts_url,
                    },
                    "created_at": s.created_at,
                }
            )

        return Response(results, status=status.HTTP_200_OK)
