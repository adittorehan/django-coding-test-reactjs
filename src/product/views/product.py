from datetime import date, datetime

from django.db.models import Min, Max
from django.views import generic

from django.views.generic import ListView

from product.models import Variant, Product, ProductVariantPrice


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class ProductListView(ListView):
    template_name = 'products/list.html'
    model = Product
    paginate_by = 2

    def get_queryset(self):
        title = self.request.GET.get('title') or ""
        variant = self.request.GET.get('variant') or ""
        price_from = self.request.GET.get('price_from') or \
                     ProductVariantPrice.objects.aggregate(Min('price'))['price__min']
        price_to = self.request.GET.get('price_to') or ProductVariantPrice.objects.aggregate(Max('price'))['price__max']
        date = self.request.GET.get('date')
        if date:
            start_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            start_date = Product.objects.aggregate(Min('created_at'))['created_at__min']
        end_date = datetime.today()
        return Product.objects.filter(
            title__icontains=title,
            productvariantprice__price__range=(price_from, price_to),
            productvariant__variant_title__contains=variant,
            created_at__range=(start_date, end_date)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).order_by('id')
        variant_list = []
        for variant in variants:
            variant_list.append({
                'id': variant.id,
                'title': variant.title,
                'product_variants': list(variant.productvariant_set.all().values('variant_title').distinct())

            })
        context['variants'] = list(variant_list)
        return context
