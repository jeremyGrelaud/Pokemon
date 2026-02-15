"""
Vues pour le système de boutique
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from myPokemonApp.models import Shop, ShopInventory, Item, Trainer, TrainerInventory, Transaction


@method_decorator(login_required, name='dispatch')
class ShopListView(generic.ListView):
    """Liste de toutes les boutiques"""
    model = Shop
    template_name = 'shop/shop_list.html'
    context_object_name = 'shops'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer = get_object_or_404(Trainer, username=self.request.user.username)
        context['trainer'] = trainer
        return context


@method_decorator(login_required, name='dispatch')
class ShopDetailView(generic.DetailView):
    """Vue détaillée d'une boutique"""
    model = Shop
    template_name = 'shop/shop_detail.html'
    context_object_name = 'shop'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer = get_object_or_404(Trainer, username=self.request.user.username)
        
        # Items disponibles
        all_inventory = self.object.inventory.all()
        
        # Filtrer par badges
        available_items = [
            inv for inv in all_inventory 
            if inv.is_available_for_trainer(trainer)
        ]
        
        # Séparer par catégories
        featured_items = [inv for inv in available_items if inv.is_featured]
        new_items = [inv for inv in available_items if inv.is_new and not inv.is_featured]
        regular_items = [inv for inv in available_items if not inv.is_featured and not inv.is_new]
        
        # Inventaire du joueur pour vente
        player_inventory = trainer.inventory.filter(quantity__gt=0)
        
        context.update({
            'trainer': trainer,
            'featured_items': featured_items,
            'new_items': new_items,
            'regular_items': regular_items,
            'player_inventory': player_inventory,
            'can_sell': player_inventory.exists()
        })
        
        return context


@login_required
@require_POST
def buy_item_api(request):
    """API pour acheter un objet"""
    try:
        data = json.loads(request.body)
        shop_inventory_id = data.get('shop_inventory_id')
        quantity = int(data.get('quantity', 1))
        
        if quantity <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Quantité invalide'
            })
        
        # Récupérer les objets
        trainer = get_object_or_404(Trainer, username=request.user.username)
        shop_inventory = get_object_or_404(ShopInventory, pk=shop_inventory_id)
        
        # Vérifications
        if not shop_inventory.is_available_for_trainer(trainer):
            return JsonResponse({
                'success': False,
                'error': f'Vous avez besoin de {shop_inventory.unlock_badge_required} badge(s)'
            })
        
        if not shop_inventory.has_stock(quantity):
            return JsonResponse({
                'success': False,
                'error': 'Stock insuffisant'
            })
        
        if not shop_inventory.can_afford(trainer, quantity):
            total_cost = shop_inventory.get_final_price() * quantity
            return JsonResponse({
                'success': False,
                'error': f'Pas assez d\'argent (coût: {total_cost}₽)'
            })
        
        # Effectuer l'achat
        unit_price = shop_inventory.get_final_price()
        total_cost = unit_price * quantity
        
        trainer.money -= total_cost
        trainer.save()
        
        # Mettre à jour le stock
        if shop_inventory.stock != -1:
            shop_inventory.stock -= quantity
            shop_inventory.save()
        
        # Ajouter à l'inventaire du joueur
        trainer_inventory, created = TrainerInventory.objects.get_or_create(
            trainer=trainer,
            item=shop_inventory.item,
            defaults={'quantity': 0}
        )
        trainer_inventory.quantity += quantity
        trainer_inventory.save()
        
        # Enregistrer la transaction
        Transaction.objects.create(
            trainer=trainer,
            shop=shop_inventory.shop,
            item=shop_inventory.item,
            transaction_type='buy',
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_cost
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{shop_inventory.item.name} x{quantity} acheté(s)!',
            'new_balance': trainer.money,
            'total_cost': total_cost,
            'item_name': shop_inventory.item.name,
            'quantity': quantity
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_POST
def sell_item_api(request):
    """API pour vendre un objet"""
    try:
        data = json.loads(request.body)
        trainer_inventory_id = data.get('trainer_inventory_id')
        quantity = int(data.get('quantity', 1))
        
        if quantity <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Quantité invalide'
            })
        
        # Récupérer les objets
        trainer = get_object_or_404(Trainer, username=request.user.username)
        trainer_inventory = get_object_or_404(
            TrainerInventory, 
            pk=trainer_inventory_id,
            trainer=trainer
        )
        
        # Vérifier la quantité
        if trainer_inventory.quantity < quantity:
            return JsonResponse({
                'success': False,
                'error': 'Vous n\'avez pas assez de cet objet'
            })
        
        # Vérifier si l'objet est vendable
        if not trainer_inventory.item.is_consumable:
            return JsonResponse({
                'success': False,
                'error': 'Cet objet ne peut pas être vendu'
            })
        
        # Calculer le prix de vente (50% du prix d'achat)
        unit_sell_price = trainer_inventory.item.price // 2
        total_sell_price = unit_sell_price * quantity
        
        # Effectuer la vente
        trainer.money += total_sell_price
        trainer.save()
        
        trainer_inventory.quantity -= quantity
        if trainer_inventory.quantity == 0:
            trainer_inventory.delete()
        else:
            trainer_inventory.save()
        
        # Enregistrer la transaction
        Transaction.objects.create(
            trainer=trainer,
            shop=None,  # Pas de boutique spécifique pour la vente
            item=trainer_inventory.item,
            transaction_type='sell',
            quantity=quantity,
            unit_price=unit_sell_price,
            total_price=total_sell_price
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{trainer_inventory.item.name} x{quantity} vendu(s)!',
            'new_balance': trainer.money,
            'total_earned': total_sell_price,
            'item_name': trainer_inventory.item.name,
            'quantity': quantity
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def transaction_history_view(request):
    """Afficher l'historique des transactions"""
    trainer = get_object_or_404(Trainer, username=request.user.username)
    
    transactions = Transaction.objects.filter(trainer=trainer)[:50]  # 50 dernières
    
    # Statistiques
    total_spent = sum(
        t.total_price for t in transactions.filter(transaction_type='buy')
    )
    total_earned = sum(
        t.total_price for t in transactions.filter(transaction_type='sell')
    )
    
    context = {
        'trainer': trainer,
        'transactions': transactions,
        'total_spent': total_spent,
        'total_earned': total_earned,
    }
    
    return render(request, 'shop/transaction_history.html', context)