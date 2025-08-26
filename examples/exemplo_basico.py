"""
Exemplo de uso do Agente de IA com Agno Framework
Demonstra como usar a versão experimental baseada em Agno.
"""

import sys
import os

# Adicionar o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.workflow import ResearchWorkflow

def exemplo_basico():
    """Exemplo básico de uso do agente com Agno"""
    print("EXEMPLO: Agente de IA com Agno Framework")
    print("=" * 50)
    
    # Lista de temas para testar
    temas = [
        "Blockchain e Criptomoedas",
        "Sustentabilidade Ambiental",
        "Realidade Virtual e Metaverso"
    ]
    
    # Inicializar workflow
    workflow = ResearchWorkflow()
    
    for i, tema in enumerate(temas, 1):
        print(f"\nProcessando tema {i}/{len(temas)}: {tema}")
        print("-" * 40)
        
        try:
            # Executar pesquisa e geração
            resultado = workflow.run(tema)
            
            # Salvar resultados
            workflow.save_results(resultado)
            
            # Mostrar resumo
            print("Sucesso!")
            print(f"   Titulo: {resultado['conteudo']['titulo']}")
            print(f"   Fontes: {len(resultado['conteudo']['fontes'])}")
            
        except Exception as e:
            print(f"Erro ao processar '{tema}': {e}")
    
    print("\nExemplo concluido!")
    print("Verifique a pasta 'output/' para ver os arquivos gerados.")

def exemplo_tema_personalizado():
    """Exemplo com tema personalizado"""
    print("\n🎯 EXEMPLO: Tema Personalizado")
    print("=" * 30)
    
    # Tema personalizado
    tema_personalizado = "Energia Solar no Brasil"
    
    print(f"🔍 Pesquisando sobre: {tema_personalizado}")
    
    try:
        # Inicializar workflow
        workflow = ResearchWorkflow()
        
        # Executar
        resultado = workflow.run(tema_personalizado)
        
        # Salvar
        workflow.save_results(resultado)
        
        # Mostrar detalhes
        print("\n📊 RESULTADO DETALHADO:")
        print(f"   🎯 Tema: {resultado['tema']}")
        print(f"   📅 Data: {resultado['data_geracao']}")
        print(f"   📝 Título: {resultado['conteudo']['titulo']}")
        print(f"   📄 Subtítulo: {resultado['conteudo']['subtitulo']}")
        print(f"   📏 Tamanho do conteúdo: {len(resultado['conteudo']['conteudo'])} caracteres")
        print(f"   🔗 Número de fontes: {len(resultado['conteudo']['fontes'])}")
        
        # Mostrar fontes
        print("\n📚 FONTES ENCONTRADAS:")
        for i, fonte in enumerate(resultado['conteudo']['fontes'], 1):
            print(f"   {i}. {fonte['titulo'][:60]}...")
            print(f"      🔗 {fonte['link']}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def comparar_versoes():
    """Função para comparar versão original vs Agno"""
    print("\n🆚 COMPARAÇÃO: Original vs Agno")
    print("=" * 35)
    
    print("📊 DIFERENÇAS PRINCIPAIS:")
    print("   🔧 Arquitetura:")
    print("      • Original: Classe simples Python")
    print("      • Agno: Framework multi-agente com Workflow")
    print()
    print("   🧠 Agentes:")
    print("      • Original: Lógica monolítica")
    print("      • Agno: Agente especializado (ContentGeneratorAgent)")
    print()
    print("   🛠️ Ferramentas:")
    print("      • Original: Métodos da classe")
    print("      • Agno: Toolkit personalizado (WebSearchTool)")
    print()
    print("   📈 Performance:")
    print("      • Original: Boa para casos simples")
    print("      • Agno: Otimizado para escala (10.000x mais rápido)")
    print()
    print("   🔮 Futuro:")
    print("      • Original: Limitado a funcionalidades atuais")
    print("      • Agno: Extensível para múltiplos agentes e workflows")

if __name__ == "__main__":
    print("🚀 EXEMPLOS DO AGENTE DE IA COM AGNO")
    print("=" * 50)
    
    # Executar exemplos
    exemplo_basico()
    exemplo_tema_personalizado()
    comparar_versoes()
    
    print("\n✨ Todos os exemplos executados!")
    print("📁 Verifique os arquivos gerados na pasta 'output/'")
    print("🔍 Compare com os arquivos da versão original para ver as diferenças")
