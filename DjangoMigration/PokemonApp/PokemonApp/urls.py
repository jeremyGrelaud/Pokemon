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
    path('login/', auth_views.LoginView.as_view(), name='account_login'),
    path('login/', auth_views.LoginView.as_view(), name='login'),  # alias
    path('logout/', auth_views.LogoutView.as_view(), name='account_logout'),
    # path("pokemonGame", views.PokemonGameLauncherView.as_view(), name='PokemonGameLauncherView'),


    # Dashboard
    path('', views.DashboardView.as_view(), name='home'),
    
    # Starter selection (nouveaux joueurs)
    path('choose-starter/', views.choose_starter_view, name='choose_starter'),
    
    # Pokédex
    path('pokedex/', views.PokemonOverView.as_view(), name='PokemonOverView'),
    path('pokemon/<int:pk>/', views.PokemonDetailView.as_view(), name='PokemonDetailView'),
    
    # Capacités
    path('moves/', views.PokemonMoveOverView.as_view(), name='PokemonMoveOverView'),
    path('move/<int:pk>/', views.PokemonMoveDetailView.as_view(), name='PokemonMoveDetailView'),
    
    # Mon équipe
    path('my-team/', views.MyTeamView.as_view(), name='MyTeamView'),
    path('api/reorder-party/', views.reorder_party_api, name='ReorderPartyAPI'),
    path('api/send-to-pc/', views.send_to_pc_api, name='SendToPCAPI'),
    path('api/add-to-party/', views.add_to_party_api, name='AddToPartyAPI'),
    path('api/pokemon/moves/', views.get_pokemon_moves_api, name='GetPokemonMovesAPI'),
    path('api/pokemon/swap-move/', views.swap_move_api, name='SwapMoveAPI'),
    
    # Combats
    path('battles/', views.BattleListView.as_view(), name='BattleListView'),
    path('battle/<int:pk>/', views.BattleDetailView.as_view(), name='BattleDetailView'),
    
    # Champions d'Arène
    path('gym-leaders/', views.GymLeaderListView.as_view(), name='GymLeaderListView'),
    path('gym-leader/<int:pk>/', views.GymLeaderDetailView.as_view(), name='GymLeaderDetailView'),
    path('badges/', views.BadgeBoxView.as_view(), name='BadgeBoxView'),
    
    # Objets
    path('items/', views.ItemListView.as_view(), name='ItemListView'),

    # Combat graphique
    path('battle/<int:pk>/play/', views.BattleGameView.as_view(), name='BattleGameView'),
    path('battle/<int:pk>/action/', views.battle_action_view, name='BattleActionView'),    
    path('battle/<int:pk>/learn-move/', views.battle_learn_move_view, name='BattlelearnMoveView'),

    # path('battle/create/', views.BattleCreateView.as_view(), name='BattleCreateView'),

    path('get_trainer_items/', views.GetTrainerItems, name='GetTrainerItems'),
    path('get_trainer_team/', views.GetTrainerTeam, name='GetTrainerTeam'),


    # Boutiques
    path('shops/', views.ShopListView.as_view(), name='ShopListView'),
    path('shop/<int:pk>/', views.ShopDetailView.as_view(), name='ShopDetailView'),
    path('api/shop/buy/', views.buy_item_api, name='BuyItemAPI'),
    path('api/shop/sell/', views.sell_item_api, name='SellItemAPI'),
    path('transactions/', views.transaction_history_view, name='TransactionHistoryView'),

    # Capture journal
    path('captures/', views.CaptureViews.capture_journal_view, name='CaptureJournalView'),


    # Centres pokemon
    path('pokemon-centers/', views.PokemonCenterListView.as_view(), name='PokemonCenterListView'),
    path('pokemon-center/<int:pk>/', views.PokemonCenterDetailView.as_view(), name='PokemonCenterDetailView'),
    path('pokemon-center/history/', views.center_history_view, name='CenterHistoryView'),
    path('api/pokemon-center/heal/', views.heal_team_api, name='HealTeamAPI'),
    path('api/pokemon-center/pc/', views.access_pc_from_center_api, name='AccessPCAPI'),

    # Sauvegardes
    path('saves/', views.save_select_view, name='save_select'),
    path('saves/create/<int:slot>/', views.save_create_view, name='save_create'),
    path('saves/load/<int:save_id>/', views.save_load_view, name='save_load'),
    path('saves/<int:save_id>/save/', views.save_game_view, name='save_game'),
    path('saves/<int:save_id>/auto-save/', views.auto_save_view, name='auto_save'),
    # API pour modal de sauvegarde
    path('saves/slots/list/', views.save_slots_list_view, name='save_slots_list'),
    path('saves/create/<int:slot>/quick/', views.save_create_quick_view, name='save_create_quick'),
    
    # Combats
    path('battle/create/', views.battle_create_view, name='BattleCreateView'),
    path('battle/wild/challenge/', views.battle_create_wild_view, name='create_wild_battle'),
    path('battle/trainer/<int:trainer_id>/challenge/', views.battle_create_trainer_view, name='battle_create_trainer'),
    path('battle/gym/challenge/', views.battle_create_gym_view, name='create_gym_battle'),
    path('battle/gym/<int:gym_leader_id>/challenge/', views.battle_challenge_gym_view, name='battle_challenge_gym'),
    path('battle/<int:battle_id>/trainer/complete/', views.battle_trainer_complete_view, name='battle_trainer_complete'),

    # Maps
    path('map/', views.map_view, name='map_view'),
    path('map/zone/<int:zone_id>/', views.zone_detail_view, name='zone_detail'),
    path('map/travel/<int:zone_id>/', views.travel_to_zone_view, name='travel_to_zone'),
    path('map/encounter/<int:zone_id>/', views.wild_encounter_view, name='wild_encounter'),

    # Bâtiments multi-étages
    path('map/zone/<int:zone_id>/building/', views.building_view, name='building_view'),
    path('map/zone/<int:zone_id>/floor/<int:floor_number>/', views.floor_detail_view, name='floor_detail'),
    path('map/zone/<int:zone_id>/floor/<int:floor_number>/encounter/', views.floor_wild_encounter_view, name='floor_encounter'),

    # Quêtes
    path('quests/', views.quest_log_view, name='quest_log'),
    path('quests/widget/', views.quest_widget_view, name='quest_widget'),
    path('quests/<str:quest_id>/', views.quest_detail_view, name='quest_detail'),

    # Achievements
    path('achievements/', views.achievements_list_view, name='achievements_list'),
    path('achievements/widget/', views.achievements_widget_view, name='achievements_widget'),


]