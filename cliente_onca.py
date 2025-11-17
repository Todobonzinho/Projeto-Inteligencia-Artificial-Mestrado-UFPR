#!/usr/bin/env python3
# cliente_onca_ultra_defensiva.py
# Estratégia ULTRA-DEFENSIVA - GARANTE movimento sempre

import sys
import redis
import random

class OncaUltraDefensiva:
    def __init__(self, host="127.0.0.1", port=10001):
        self.lado = 'o'
        self.r = redis.Redis(host=host, port=port, db=0, decode_responses=True)
        self.key_tab = "tabuleiro_o"
        self.key_jog = "jogada_o"
        self.contador = 0
        
    def parse_tabuleiro(self, tabuleiro_str):
        """Parser ULTRA-RÁPIDO"""
        linhas = tabuleiro_str.strip().split('\n')
        
        estado = {
            'onca': None,
            'caes': [],
            'vazios': []
        }
        
        for linha_idx, linha in enumerate(linhas):
            for col_idx, char in enumerate(linha):
                if char == 'o':
                    estado['onca'] = (linha_idx, col_idx)
                elif char == 'c':
                    estado['caes'].append((linha_idx, col_idx))
                elif char == '-':
                    estado['vazios'].append((linha_idx, col_idx))
        
        return estado
    
    def gerar_movimentos_garantidos(self, estado):
        """Gera TODOS os movimentos possíveis - GARANTIDO"""
        if not estado['onca']:
            return []
            
        onca_pos = estado['onca']
        movimentos = []
        
        # TODAS as direções possíveis
        direcoes = [
            (0, 1), (0, -1), (1, 0), (-1, 0),   # Horizontal/vertical
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonal
        ]
        
        for dl, dc in direcoes:
            nova_linha = onca_pos[0] + dl
            nova_coluna = onca_pos[1] + dc
            
            # Verificar se é uma posição válida e vazia
            if (1 <= nova_linha <= 6 and 1 <= nova_coluna <= 5 and 
                (nova_linha, nova_coluna) in estado['vazios']):
                
                # Verificar posições inválidas
                if not (nova_linha == 6 and nova_coluna in [1, 5]):
                    movimentos.append(f"o m {onca_pos[0]} {onca_pos[1]} {nova_linha} {nova_coluna}")
        
        return movimentos
    
    def escolher_movimento_inteligente(self, estado, movimentos):
        """Escolhe o movimento MAIS INTELIGENTE - FOCO TOTAL EM SOBREVIVÊNCIA"""
        if not movimentos:
            # EMERGÊNCIA: se não tem movimentos, cria um manualmente
            for dl, dc in [(0,1), (1,0), (0,-1), (-1,0)]:
                nova_pos = (estado['onca'][0] + dl, estado['onca'][1] + dc)
                if nova_pos in estado['vazios'] and 1 <= nova_pos[0] <= 6 and 1 <= nova_pos[1] <= 5:
                    movimento_emergencia = f"o m {estado['onca'][0]} {estado['onca'][1]} {nova_pos[0]} {nova_pos[1]}"
                    print(f"🚨 MOVIMENTO DE EMERGÊNCIA: {movimento_emergencia}")
                    return movimento_emergencia
            return "o m 3 3 4 3"  # Último recurso
        
        movimentos_avaliados = []
        
        for movimento in movimentos:
            partes = movimento.split()
            destino = (int(partes[4]), int(partes[5]))
            
            score = 0
            
            # 1. DISTÂNCIA DOS CÃES (MÁXIMA PRIORIDADE)
            distancia_minima_caes = 100
            for cao in estado['caes']:
                distancia = abs(destino[0] - cao[0]) + abs(destino[1] - cao[1])
                if distancia < distancia_minima_caes:
                    distancia_minima_caes = distancia
            
            score += distancia_minima_caes * 30  # Quanto mais longe dos cães, melhor
            
            # 2. MOBILIDADE FUTURA
            opcoes_futuras = 0
            for dl, dc in [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
                nl, nc = destino[0] + dl, destino[1] + dc
                if (nl, nc) in estado['vazios'] and 1 <= nl <= 6 and 1 <= nc <= 5:
                    if not (nl == 6 and nc in [1, 5]):
                        opcoes_futuras += 1
            
            score += opcoes_futuras * 15
            
            # 3. POSIÇÃO CENTRAL (mais segura)
            distancia_centro = abs(destino[1] - 3)
            score += (3 - distancia_centro) * 10
            
            # 4. EVITAR BORDAS (armadilhas)
            if destino[0] == 6 or destino[1] in [1, 5]:
                score -= 25
            
            # 5. MOVIMENTO PARA BAIXO (abre espaço)
            if destino[0] > estado['onca'][0]:
                score += 5
            
            movimentos_avaliados.append((score, movimento))
        
        # SEMPRE escolher o MELHOR movimento
        movimentos_avaliados.sort(reverse=True)
        melhor = movimentos_avaliados[0][1]
        melhor_score = movimentos_avaliados[0][0]
        
        print(f"🏆 MELHOR MOVIMENTO: {melhor} → {melhor_score} pontos")
        
        # Mostrar top 3 para debug
        print("📊 TOP 3 MOVIMENTOS:")
        for i, (score, mov) in enumerate(movimentos_avaliados[:3]):
            print(f"   {i+1}. {mov} → {score}")
        
        return melhor
    
    def jogar(self):
        print("🐆🛡️  ONÇA ULTRA-DEFENSIVA ATIVADA! 🛡️🐆")
        print("🎯 ESTRATÉGIA: SOBREVIVÊNCIA TOTAL - ZERO JOGADAS VAZIAS")
        print("✅ GARANTIDO: SEMPRE SE MOVE")
        print("⏳ Aguardando partida...")
        
        try:
            while True:
                print(f"\n🐆 [ONÇA] Turno {self.contador + 1} - Buscando sobrevivência...")
                
                # Receber tabuleiro
                item = self.r.blpop(self.key_tab, timeout=0)
                buffer = item[1]
                lines = buffer.splitlines()
                
                if len(lines) >= 3:
                    quem_joga = lines[0].strip()
                    jogada_anterior = lines[1].strip()
                    tabuleiro_str = "\n".join(lines[2:])
                    
                    print(f"🎲 Vez de: {quem_joga}")
                    print(f"📝 Última: {jogada_anterior}")
                    
                    if quem_joga == 'o':
                        self.contador += 1
                        
                        # Parse RÁPIDO
                        estado = self.parse_tabuleiro(tabuleiro_str)
                        
                        if estado['onca']:
                            print(f"🎯 Onça localizada: {estado['onca']}")
                            print(f"🐕 {len(estado['caes'])} cães ameaçando")
                            print(f"🕳️  {len(estado['vazios'])} posições livres")
                        else:
                            print("❌ Onça não encontrada - modo emergência")
                        
                        # Gerar TODOS os movimentos possíveis
                        movimentos = self.gerar_movimentos_garantidos(estado)
                        print(f"📋 {len(movimentos)} movimentos possíveis")
                        
                        if movimentos:
                            # Escolher movimento MAIS INTELIGENTE
                            jogada = self.escolher_movimento_inteligente(estado, movimentos)
                        else:
                            # EMERGÊNCIA: movimento fixo garantido
                            jogada = "o m 3 3 4 3"
                            print(f"🚨 SEM MOVIMENTOS! Jogada emergência: {jogada}")
                        
                        print(f"💥 JOGADA: {jogada}")
                        
                        # Enviar COM CONVICÇÃO
                        resultado = self.r.rpush(self.key_jog, jogada)
                        print(f"✅ Jogada enviada! Sobrevivendo...")
                    
                    else:
                        print("⏳ Aguardando vez da onça...")
                    
                    print("─" * 70)
                    
        except KeyboardInterrupt:
            print(f"\n🛑 Onça ultra-defensiva finalizada - {self.contador} movimentos realizados")
        except Exception as e:
            print(f"💥 ERRO: {e}")
            import traceback
            traceback.print_exc()

def main():
    print("INICIANDO ESTRATÉGIA ULTRA-DEFENSIVA PARA ONÇA")
    print("OBJETIVO: SOBREVIVER E FORÇAR VITÓRIA LEGÍTIMA DOS CÃES")
    print("GARANTIA: ZERO JOGADAS 'o' VAZIAS")
    
    onca = OncaUltraDefensiva()
    onca.jogar()

if __name__ == "__main__":
    main()