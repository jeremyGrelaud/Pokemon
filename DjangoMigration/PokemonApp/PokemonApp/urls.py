"""
URL configuration for PokemonApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myPokemonApp import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='account_login'), #base django login and logout
    path('logout/', auth_views.LogoutView.as_view(), name='account_logout'),
    # path("pokemonGame", views.PokemonGameLauncherView.as_view(), name='PokemonGameLauncherView'),


    # Dashboard
    path('', views.DashboardView.as_view(), name='home'),
    
    # Pokédex
    path('pokedex/', views.PokemonOverView.as_view(), name='PokemonOverView'),
    path('pokemon/<int:pk>/', views.PokemonDetailView.as_view(), name='PokemonDetailView'),
    
    # Capacités
    path('moves/', views.PokemonMoveOverView.as_view(), name='PokemonMoveOverView'),
    path('move/<int:pk>/', views.PokemonMoveDetailView.as_view(), name='PokemonMoveDetailView'),
    
    # Mon équipe
    path('my-team/', views.MyTeamView.as_view(), name='MyTeamView'),
    
    # Combats
    path('battles/', views.BattleListView.as_view(), name='BattleListView'),
    path('battle/<int:pk>/', views.BattleDetailView.as_view(), name='BattleDetailView'),
    
    # Champions d'Arène
    path('gym-leaders/', views.GymLeaderListView.as_view(), name='GymLeaderListView'),
    path('gym-leader/<int:pk>/', views.GymLeaderDetailView.as_view(), name='GymLeaderDetailView'),
    
    # Objets
    path('items/', views.ItemListView.as_view(), name='ItemListView'),

    # Combat graphique
    path('battle/<int:pk>/play/', views.BattleGameView.as_view(), name='BattleGameView'),
    path('battle/<int:pk>/action/', views.battle_action_view, name='BattleActionView'),    

    path('battle/create/', views.BattleCreateView.as_view(), name='BattleCreateView'),

    path('get_trainer_items/', views.GetTrainerItems, name='GetTrainerItems'),
    path('get_trainer_team/', views.GetTrainerTeam, name='GetTrainerTeam'),


    # NOUVELLES ROUTES API
    path('api/heal-pokemon/', views.heal_pokemon_api, name='HealPokemonAPI'),
    path('api/heal-all-pokemon/', views.heal_all_pokemon_api, name='HealAllPokemonAPI'),
    path('api/send-to-pc/', views.send_to_pc_api, name='SendToPCAPI'),
    path('api/add-to-party/', views.add_to_party_api, name='AddToPartyAPI'),

    # Boutiques
    path('shops/', views.ShopListView.as_view(), name='ShopListView'),
    path('shop/<int:pk>/', views.ShopDetailView.as_view(), name='ShopDetailView'),
    path('api/shop/buy/', views.buy_item_api, name='BuyItemAPI'),
    path('api/shop/sell/', views.sell_item_api, name='SellItemAPI'),
    path('transactions/', views.transaction_history_view, name='TransactionHistoryView'),



    # Liste des centres
    path('pokemon-centers/', views.PokemonCenterListView.as_view(), name='PokemonCenterListView'),
    # Détails d'un centre
    path('pokemon-center/<int:pk>/', views.PokemonCenterDetailView.as_view(), name='PokemonCenterDetailView'),
    # API - Soigner l'équipe
    path('api/pokemon-center/heal/', views.heal_team_api, name='HealTeamAPI'),
    # API - Accès PC
    path('api/pokemon-center/pc/', views.access_pc_from_center_api, name='AccessPCAPI'),
    # Historique
    path('pokemon-center/history/', views.center_history_view, name='CenterHistoryView'),
]