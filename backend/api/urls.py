from django.urls import path

from api import views

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    # Products & categories
    path("categories/", views.CategoryListView.as_view(), name="categories"),
    path("products/", views.ProductsByCategoryView.as_view(), name="products-by-category"),
    path("products/search/", views.ProductSearchView.as_view(), name="product-search"),
    path("products/<str:product_id>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("products/barcode/<str:barcode>/", views.ProductByBarcodeView.as_view(), name="product-by-barcode"),
    path("products/barcode/<str:barcode>/fetch/", views.ProductFetchByBarcodeView.as_view(), name="product-fetch-by-barcode"),
    path("products/barcode/<str:barcode>/test/", views.ProductTestByBarcodeView.as_view(), name="product-test-by-barcode"),
    path("products/name/<str:search_terms>/", views.ProductSearchByNameView.as_view(), name="product-search-by-name"),
    # Substitutions
    path("substitutions/", views.SubstitutionListView.as_view(), name="substitution-list"),
    path("substitutions/find/", views.SubstitutionFindView.as_view(), name="substitution-find"),
    path("substitutions/save/", views.SubstitutionSaveView.as_view(), name="substitution-save"),
    path("substitutions/my/", views.MySubstitutionsView.as_view(), name="substitution-my"),
    # Auth
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]

