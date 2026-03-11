// ============================================================
// utils/EventBus.ts
// Bus d'événements partagé entre toutes les scènes Phaser.
// Utilise EventEmitter de Phaser pour rester cohérent.
// ============================================================

import Phaser from 'phaser'
import type { GameEvent } from '@/types'

// Instance unique partagée par toutes les scènes
export const EventBus = new Phaser.Events.EventEmitter()

// Helper typé pour émettre des événements du jeu
export function emit(event: GameEvent, ...args: unknown[]): void {
  EventBus.emit(event, ...args)
}

// Helper typé pour écouter des événements
export function on(
  event: GameEvent,
  callback: (...args: unknown[]) => void,
  context?: unknown
): void {
  EventBus.on(event, callback, context)
}

export function off(
  event: GameEvent,
  callback: (...args: unknown[]) => void,
  context?: unknown
): void {
  EventBus.off(event, callback, context)
}
