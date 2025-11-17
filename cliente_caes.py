#!/usr/bin/env python3
# cliente_caes_cerco_inteligente.py
# Estratégia de CERCO INTELIGENTE - Foco em BLOQUEAR movimentos da onça

import sys
import redis
import random

class CaesCercoInteligente:
    def __init__(self, host="127.0.0.1", port=10001):
        self.lado = 'c'
        self.r = redis.Redis(host=host, port=port, db=0, decode_responses=True)
        self.key_tab = "tabuleiro_c"
        self.key_jog = "jogada_c"
        self.contador = 0
        
    def parse_tabuleiro(self, tabuleiro_str):
        """Parser rápido e eficiente"""
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
    
    def calcular_movimentos_onca(self, estado, posicao_onca):
        """Calcula TODOS os movimentos possíveis da onça numa posição"""
        movimentos_onca = []
        direcoes = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        
        for dl, dc in direcoes:
            nl, nc = posicao_onca[0] + dl, posicao_onca[1] + dc
            if (nl, nc) in estado['vazios'] and 1 <= nl <= 6 and 1 <= nc <= 5:
                if not (nl == 6 and nc in [1, 5]):
                    movimentos_onca.append((nl, nc))
        
        return movimentos_onca
    
    def gerar_jogadas_cerco_eficiente(self, estado):
        """Gera jogadas que BLOQUEIAM os movimentos da onça"""
        if not estado['onca']:
            return []
            
        onca_pos = estado['onca']
        jogadas = []
        
        # 1. PRIMEIRO: Bloquear movimentos da onça
        movimentos_onca = self.calcular_movimentos_onca(estado, onca_pos)
        
        print(f"🎯 Onça em {onca_pos} pode mover para: {movimentos_onca}")
        
        # Para cada movimento possível da onça, tentar bloqueá-lo
        for movimento in movimentos_onca:
            # Encontrar cães que podem bloquear este movimento
            for cao in estado['caes']:
                # Verificar se este cão pode se mover para bloquear
                if self.pode_mover_para(cao, movimento, estado):
                    jogada = f"c m {cao[0]} {cao[1]} {movimento[0]} {movimento[1]}"
                    if jogada not in jogadas:
                        jogadas.append(jogada)
        
        # 2. SEGUNDO: Se não conseguiu bloquear, cercar progressivamente
        if not jogadas:
            posicoes_cerco = self.calcular_posicoes_cerco(estado, onca_pos)
            for pos in posicoes_cerco:
                for cao in estado['caes']:
                    if self.pode_mover_para(cao, pos, estado):
                        jogada = f"c m {cao[0]} {cao[1]} {pos[0]} {pos[1]}"
                        if jogada not in jogadas:
                            jogadas.append(jogada)
        
        # 3. TERCEIRO: Movimentos básicos se ainda não encontrou
        if not jogadas:
            # Movimentos do topo para baixo (sempre úteis)
            movimentos_basicos = [
                "c m 1 1 2 1", "c m 1 2 2 2", "c m 1 3 2 3", "c m 1 4 2 4", "c m 1 5 2 5",
                "c m 2 1 3 1", "c m 2 2 3 2", "c m 2 3 3 3", "c m 2 4 3 4", "c m 2 5 3 5",
            ]
            
            for jogada in movimentos_basicos:
                partes = jogada.split()
                origem = (int(partes[2]), int(partes[3]))
                destino = (int(partes[4]), int(partes[5]))
                
                if origem in estado['caes'] and destino in estado['vazios']:
                    jogadas.append(jogada)
        
        return jogadas
    
    def pode_mover_para(self, origem, destino, estado):
        """Verifica se um cão pode se mover para uma posição"""
        if destino not in estado['vazios']:
            return False
        
        # Verificar distância (movimento adjacente)
        dist_linha = abs(destino[0] - origem[0])
        dist_coluna = abs(destino[1] - origem[1])
        
        if dist_linha > 1 or dist_coluna > 1:
            return False
        
        # Verificar se é posição válida
        if not (1 <= destino[0] <= 6 and 1 <= destino[1] <= 5):
            return False
            
        if destino[0] == 6 and destino[1] in [1, 5]:
            return False
            
        return True
    
    def calcular_posicoes_cerco(self, estado, onca_pos):
        """Calcula as melhores posições para cercar a onça"""
        posicoes_cerco = []
        
        # Posições em volta da onça (círculo de cerco)
        direcoes = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        
        for dl, dc in direcoes:
            nl, nc = onca_pos[0] + dl, onca_pos[1] + dc
            if (nl, nc) in estado['vazios'] and 1 <= nl <= 6 and 1 <= nc <= 5:
                if not (nl == 6 and nc in [1, 5]):
                    posicoes_cerco.append((nl, nc))
        
        # Ordenar por proximidade (mais perto primeiro)
        posicoes_cerco.sort(key=lambda pos: abs(pos[0]-onca_pos[0]) + abs(pos[1]-onca_pos[1]))
        
        return posicoes_cerco
    
    def escolher_jogada_cerco(self, estado, jogadas):
        """Escolhe a jogada que MAIS BLOQUEIA a onça"""
        if not jogadas:
            # EMERGÊNCIA: movimento básico garantido
            for cao in estado['caes']:
                for dl, dc in [(0,1), (1,0)]:
                    destino = (cao[0] + dl, cao[1] + dc)
                    if destino in estado['vazios'] and 1 <= destino[0] <= 6 and 1 <= destino[1] <= 5:
                        return f"c m {cao[0]} {cao[1]} {destino[0]} {destino[1]}"
            return "c m 1 1 2 1"
        
        # Avaliar cada jogada pelo nível de bloqueio
        jogadas_avaliadas = []
        
        for jogada in jogadas:
            partes = jogada.split()
            destino = (int(partes[4]), int(partes[5]))
            onca_pos = estado['onca']
            
            score = 0
            
            # 1. BLOQUEIO DIRETO (MÁXIMA PRIORIDADE)
            # Verificar se esta posição bloqueia um movimento da onça
            movimentos_onca = self.calcular_movimentos_onca(estado, onca_pos)
            if destino in movimentos_onca:
                score += 100  # BLOQUEIO DIRETO!
            
            # 2. PROXIMIDADE DA ONÇA
            distancia = abs(destino[0] - onca_pos[0]) + abs(destino[1] - onca_pos[1])
            if distancia == 1:
                score += 50   # Adjacente à onça
            elif distancia == 2:
                score += 25   # Dois passos
            
            # 3. POSIÇÃO ESTRATÉGICA
            # Posições que forçam a onça para cantos
            if destino[0] > onca_pos[0]:  # Abaixo da onça
                score += 10
            if destino[1] == 3:  # Centro vertical
                score += 5
            
            jogadas_avaliadas.append((score, jogada))
        
        # Escolher a jogada com MELHOR BLOQUEIO
        jogadas_avaliadas.sort(reverse=True)
        melhor = jogadas_avaliadas[0][1]
        melhor_score = jogadas_avaliadas[0][0]
        
        print(f"🏆 MELHOR BLOQUEIO: {melhor} → {melhor_score} pontos")
        
        # Mostrar estratégia
        if melhor_score >= 100:
            print("   🚫 BLOQUEIO DIRETO - Movimento da onça impedido!")
        elif melhor_score >= 50:
            print("   📍 CERCO APROXIMADO - Adjacente à onça")
        else:
            print("   🎯 POSIÇÃO ESTRATÉGICA - Preparando cerco")
        
        return melhor
    
    def jogar(self):
        print("🐺🎯 CÃES DE CERCO INTELIGENTE ATIVADOS! 🎯🐺")
        print("🎯 ESTRATÉGIA: BLOQUEIO SISTEMÁTICO + CERCO PROGRESSIVO")
        print("⛔ OBJETIVO: IMPEDIR TODOS OS MOVIMENTOS DA ONÇA")
        print("⏳ Iniciando operação de cerco...")
        
        try:
            while True:
                print(f"\n🐕 [CÃES] Turno {self.contador + 1} - Executando cerco...")
                
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
                    
                    if quem_joga == 'c':
                        self.contador += 1
                        
                        # Parse do tabuleiro
                        estado = self.parse_tabuleiro(tabuleiro_str)
                        
                        if estado['onca']:
                            print(f"🎯 ALVO LOCALIZADO: Onça em {estado['onca']}")
                            
                            # Analisar situação atual
                            movimentos_onca = self.calcular_movimentos_onca(estado, estado['onca'])
                            print(f"📊 Onça tem {len(movimentos_onca)} movimentos possíveis")
                            
                            if len(movimentos_onca) == 0:
                                print("🚨 VITÓRIA IMINENTE: Onça está ENCURRALADA!")
                        
                        # Gerar jogadas de CERCO INTELIGENTE
                        jogadas = self.gerar_jogadas_cerco_eficiente(estado)
                        print(f"📋 {len(jogadas)} jogadas de cerco identificadas")
                        
                        # Escolher jogada de BLOQUEIO MÁXIMO
                        jogada = self.escolher_jogada_cerco(estado, jogadas)
                        
                        print(f"💥 JOGADA DE CERCO: {jogada}")
                        
                        # Executar
                        self.r.rpush(self.key_jog, jogada)
                        print("✅ Cerco em andamento...")
                    
                    else:
                        print("⏳ Aguardando vez do cerco...")
                    
                    print("─" * 70)
                    
        except KeyboardInterrupt:
            print(f"\n🛑 Operação de cerco finalizada - {self.contador} cercos executados")
        except Exception as e:
            print(f"💥 ERRO: {e}")
            import traceback
            traceback.print_exc()

def main():
    print("INICIANDO ESTRATÉGIA DE CERCO INTELIGENTE")
    print("OBJETIVO: VITÓRIA EM 100% DAS PARTIDAS")
    print("TÁTICA: BLOQUEIO SISTEMÁTICO + CERCO IMPLACÁVEL")
    
    caes = CaesCercoInteligente()
    caes.jogar()

if __name__ == "__main__":
    main()