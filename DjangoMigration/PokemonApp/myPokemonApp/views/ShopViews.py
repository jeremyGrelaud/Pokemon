"""
Vues pour le système de boutique
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Q
import json

from myPokemonApp.models import Shop, ShopInventory, Item, Trainer, TrainerInventory, Transaction
from django.contrib import messages
from myPokemonApp.gameUtils import (
    get_player_trainer,
    trainer_is_at_zone_with,
    give_item_to_trainer,
    remove_item_from_trainer,
)


def _location_guard(request, zone_attr, redirect_name='map_view', warning_msg=None):
    """
    Helper interne : recupere le trainer et verifie sa localisation.
    Retourne (trainer, None) si OK, (None, redirect_response) sinon.
    """
    trainer = get_player_trainer(request.user)
    if not trainer_is_at_zone_with(trainer, zone_attr):
        messages.warning(request, warning_msg or "Vous n'êtes pas au bon endroit.")
        return None, redirect(redirect_name)
    return trainer, None


@method_decorator(login_required, name='dispatch')
class ShopListView(generic.ListView):
    model = Shop
    template_name = 'shop/shop_list.html'
    context_object_name = 'shops'

    def dispatch(self, request, *args, **kwargs):
        trainer, redir = _location_guard(
            request, 'has_shop', 'map_view',
            "Vous devez être dans une ville possédant une boutique pour y accéder."
        )
        if redir:
            return redir
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trainer'] = get_player_trainer(self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
class ShopDetailView(generic.DetailView):
    """Vue détaillée d'une boutique"""
    model = Shop
    template_name = 'shop/shop_detail.html'
    context_object_name = 'shop'

    def dispatch(self, request, *args, **kwargs):
        trainer, redir = _location_guard(
            request, 'has_shop', 'map_view',
            "Vous devez être dans une ville possédant une boutique pour y accéder."
        )
        if redir:
            return redir
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer = get_player_trainer(self.request.user)

        all_inventory = self.object.inventory.all()
        available_items = [inv for inv in all_inventory if inv.is_available_for_trainer(trainer)]

        featured_items = [inv for inv in available_items if inv.is_featured]
        new_items      = [inv for inv in available_items if inv.is_new and not inv.is_featured]
        regular_items  = [inv for inv in available_items if not inv.is_featured and not inv.is_new]

        player_inventory = trainer.inventory.filter(quantity__gt=0)

        context.update({
            'trainer':        trainer,
            'featured_items': featured_items,
            'new_items':      new_items,
            'regular_items':  regular_items,
            'player_inventory': player_inventory,
            'can_sell':       player_inventory.exists(),
        })
        return context


@login_required
@require_POST
def buy_item_api(request):
    """API pour acheter un objet"""
    try:
        data              = json.loads(request.body)
        shop_inventory_id = data.get('shop_inventory_id')
        quantity          = int(data.get('quantity', 1))

        if quantity <= 0:
            return JsonResponse({'success': False, 'error': 'Quantité invalide'})

        trainer        = get_player_trainer(request.user)
        shop_inventory = get_object_or_404(ShopInventory, pk=shop_inventory_id)

        if not shop_inventory.is_available_for_trainer(trainer):
            return JsonResponse({
                'success': False,
                'error': f'Vous avez besoin de {shop_inventory.unlock_badge_required} badge(s)'
            })

        if not shop_inventory.has_stock(quantity):
            return JsonResponse({'success': False, 'error': 'Stock insuffisant'})

        if not shop_inventory.can_afford(trainer, quantity):
            total_cost = shop_inventory.get_final_price() * quantity
            return JsonResponse({
                'success': False,
                'error': f"Pas assez d'argent (coût: {total_cost}₽)"
            })

        unit_price = shop_inventory.get_final_price()
        total_cost = unit_price * quantity

        # Trainer.spend_money gère le .save()
        trainer.spend_money(total_cost)

        if shop_inventory.stock != -1:
            shop_inventory.stock -= quantity
            shop_inventory.save()

        # give_item_to_trainer gère le get_or_create + incrémentation
        give_item_to_trainer(trainer, shop_inventory.item, quantity)

        Transaction.objects.create(
            trainer=trainer,
            shop=shop_inventory.shop,
            item=shop_inventory.item,
            transaction_type='buy',
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_cost,
        )

        return JsonResponse({
            'success':     True,
            'message':     f'{shop_inventory.item.name} x{quantity} acheté(s)!',
            'new_balance': trainer.money,
            'total_cost':  total_cost,
            'item_name':   shop_inventory.item.name,
            'quantity':    quantity,
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def sell_item_api(request):
    """API pour vendre un objet"""
    try:
        data                 = json.loads(request.body)
        trainer_inventory_id = data.get('trainer_inventory_id')
        quantity             = int(data.get('quantity', 1))

        if quantity <= 0:
            return JsonResponse({'success': False, 'error': 'Quantité invalide'})

        trainer           = get_player_trainer(request.user)
        trainer_inventory = get_object_or_404(
            TrainerInventory, pk=trainer_inventory_id, trainer=trainer
        )

        if trainer_inventory.quantity < quantity:
            return JsonResponse({'success': False, 'error': "Vous n'avez pas assez de cet objet"})

        if not trainer_inventory.item.is_consumable:
            return JsonResponse({'success': False, 'error': "Cet objet ne peut pas être vendu"})

        unit_sell_price  = trainer_inventory.item.price // 2
        total_sell_price = unit_sell_price * quantity

        # Trainer.earn_money gère le .save()
        trainer.earn_money(total_sell_price)

        # remove_item_from_trainer gère la décrémentation + suppression si 0
        remove_item_from_trainer(trainer, trainer_inventory.item, quantity)

        Transaction.objects.create(
            trainer=trainer,
            shop=None,
            item=trainer_inventory.item,
            transaction_type='sell',
            quantity=quantity,
            unit_price=unit_sell_price,
            total_price=total_sell_price,
        )

        return JsonResponse({
            'success':      True,
            'message':      f'{trainer_inventory.item.name} x{quantity} vendu(s)!',
            'new_balance':  trainer.money,
            'total_earned': total_sell_price,
            'item_name':    trainer_inventory.item.name,
            'quantity':     quantity,
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def transaction_history_view(request):
    """Afficher l'historique des transactions"""
    trainer      = get_player_trainer(request.user)
    transactions = Transaction.objects.filter(trainer=trainer).order_by('-created_at')[:50]

    # Agrégation en DB au lieu de deux sum() Python
    agg = Transaction.objects.filter(trainer=trainer).aggregate(
        total_spent=Sum('total_price', filter=Q(transaction_type='buy')),
        total_earned=Sum('total_price', filter=Q(transaction_type='sell')),
    )

    context = {
        'trainer':      trainer,
        'transactions': transactions,
        'total_spent':  agg['total_spent'] or 0,
        'total_earned': agg['total_earned'] or 0,
    }
    return render(request, 'shop/transaction_history.html', context)