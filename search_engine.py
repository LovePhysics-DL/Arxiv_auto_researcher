import os
import arxiv
import logging
from openai import OpenAI
from dataclasses import dataclass

@dataclass
class Config:
    max_results: int = 10
    sort_by: arxiv.SortCriterion = arxiv.SortCriterion.SubmittedDate
    model_name: str = "Qwen/Qwen3-30B-A3B-Thinking-2507"
    base_url: str = 'https://api-inference.modelscope.cn/v1'
    api_key: str = 'ms-a82f12ea-6d04-4bbe-aa94-8a46c2050d88'


class LLMQueryGenerator:
    def __init__(self,config:Config):
        self.config = config
        self.client = OpenAI(
            base_url=self.config.base_url,
            api_key=self.config.api_key

        )
        self.__setup_logging()
    
    def __setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)  
    
    def build_prompt(self, user_input: str, strategy: str = "balanced") -> str:
        if strategy == "broad":
            return f"""
# 角色设定
你是一个专业的学术文献搜索助手，专门生成符合 arXiv 搜索语法的查询字符串。

# 任务目标 - 宽泛搜索策略
根据用户描述，生成一个宽泛的查询字符串，优先保证能找到相关文献，宁可多找也不要漏掉。

# 输出格式要求
- 生成符合 arXiv 搜索语法的英文查询字符串
- 优先使用 OR 连接同义词和相关概念
- 减少 AND 条件，避免过于严格
- 使用更通用的关键词
- 只输出查询字符串，不要解释

用户输入：{user_input}
输出：
"""
        elif strategy == "precise":
            return f"""
# 角色设定
你是一个专业的学术文献搜索助手，专门生成符合 arXiv 搜索语法的查询字符串。

# 任务目标 - 精确搜索策略
根据用户描述，生成一个精确的查询字符串，重点关注最相关的文献。

# 输出格式要求
- 生成符合 arXiv 搜索语法的英文查询字符串
- 使用精确的专业术语
- 合理使用 AND 和 OR
- 可以使用 title: 和 abstract: 前缀提高精度
- 只输出查询字符串，不要解释

用户输入：{user_input}
输出：
"""
        else:  # balanced
            return f"""
# 角色设定
你是一个专业的学术文献搜索助手，专门生成符合 arXiv 搜索语法的查询字符串。

# 任务目标
根据用户的中文或英文描述，生成一个既能检索到相关文献，又能保证检索结果强相关的 arXiv 搜索查询字符串。请综合考虑召回率和精准度，合理使用 AND 和 OR，避免条件过于严格导致无结果，也避免过于宽泛导致无关文献过多。

# 输出格式要求
- 生成符合 arXiv 搜索语法的英文查询字符串。
- 关键词和短语请用英文，使用双引号""进行精确短语匹配。
- 合理使用 AND、OR、NOT 连接关键词，优先包含核心概念和专业术语。
- 可使用前缀：title:, abstract:, author:, cat:，以提升相关性。
- 查询应简洁、准确且具有针对性，避免过多无关词。
- 如果用户输入涉及多个核心概念，建议主概念用 AND，相关同义词用 OR。
- 只输出最终的查询字符串，不要任何解释或说明。

# 示例
用户输入：深度学习用于图像分类
输出：("deep learning" OR "neural network") AND ("image classification" OR "computer vision")

用户输入：transformer在自然语言处理中的应用
输出：("transformer" OR "attention mechanism") AND ("natural language processing" OR "NLP")

用户输入：单细胞RNA测序数据分析
输出：("single-cell RNA sequencing" OR "scRNA-seq") AND ("data analysis" OR "computational biology")

# 实际任务
用户输入：{user_input}
输出（仅返回查询字符串，不要其他解释）：
"""

    def generate_query(self, user_input: str, strategy: str = "balanced"):
        prompt = self.build_prompt(user_input, strategy)
        self.logger.info(f"正在为输入 '{user_input}' 生成查询... (策略: {strategy})")
        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            temperature=0.2,
        )
        query = response.choices[0].message.content.strip()
        self.logger.info(f"生成的查询: {query}")
        return query
    
    def search_arxiv(self, query: str):
        search = arxiv.Search(
            query=query,
            max_results=self.config.max_results,
            sort_by=self.config.sort_by
        )
        return search
    
    def smart_search(self, user_input: str, enable_restructure: bool = True):
        """
        智能搜索：依次尝试不同策略，如果找不到文献则重构查询再试
        """
        original_input = user_input
        
        # 第一轮：使用原始查询尝试所有策略
        result = self._try_all_strategies(user_input, round_name="原始查询")
        
        # 如果找到足够文献，直接返回
        if result['count'] >= 1:
            return result
        
        # 如果启用查询重构且第一轮没找到文献，进行查询重构
        if enable_restructure and result['count'] == 0:
            self.logger.info("原始查询未找到文献，正在进行查询重构...")
            
            # 重构查询（获取多个策略）
            restructured_queries = self.restructure_query(original_input)
            
            # 尝试每个重构策略
            for i, restructured_input in enumerate(restructured_queries, 1):
                if restructured_input == original_input:
                    continue  # 跳过与原查询相同的
                    
                self.logger.info(f"尝试重构策略 {i}: {restructured_input}")
                
                # 使用重构后的查询尝试所有策略
                restructured_result = self._try_all_strategies(
                    restructured_input, 
                    round_name=f"重构策略{i}"
                )
                
                if restructured_result['count'] > 0:
                    # 添加重构信息到结果中
                    restructured_result['original_query'] = original_input
                    restructured_result['restructured_query'] = restructured_input
                    restructured_result['restructure_strategy'] = i
                    restructured_result['used_restructure'] = True
                    self.logger.info(f"重构策略 {i} 成功找到 {restructured_result['count']} 篇文献")
                    return restructured_result
            
            self.logger.warning("所有查询重构策略均未找到相关文献")
        
        # 如果所有尝试都失败，返回最好的结果
        result['original_query'] = original_input
        result['used_restructure'] = False
        return result
    
    def _try_all_strategies(self, user_input: str, round_name: str = ""):
        """尝试所有搜索策略"""
        self.logger.info(f"开始 {round_name} 搜索...")
        strategies = ["balanced", "broad", "precise"]
        results = []
        
        for strategy in strategies:
            self.logger.info(f"尝试 {strategy} 搜索策略...")
            
            query = self.generate_query(user_input, strategy)
            search = self.search_arxiv(query)
            
            # 收集结果
            strategy_results = []
            try:
                for paper in search.results():
                    strategy_results.append({
                        'title': paper.title,
                        'authors': [author.name for author in paper.authors],
                        'summary': paper.summary,
                        'published': paper.published,
                        'url': paper.entry_id,
                        'pdf_url': paper.pdf_url,
                        'categories': paper.categories
                    })
                
                self.logger.info(f"{strategy} 策略找到 {len(strategy_results)} 篇文献")
                
                if len(strategy_results) >= 3:  # 如果找到足够的文献就停止
                    return {
                        'strategy': strategy,
                        'query': query,
                        'results': strategy_results,
                        'count': len(strategy_results),
                        'search_input': user_input
                    }
                elif len(strategy_results) > 0:  # 保存结果但继续尝试其他策略
                    results.append({
                        'strategy': strategy,
                        'query': query,
                        'results': strategy_results,
                        'count': len(strategy_results),
                        'search_input': user_input
                    })
                    
            except Exception as e:
                self.logger.error(f"{strategy} 策略搜索失败: {e}")
                continue
        
        # 如果所有策略都没找到足够的文献，返回找到最多结果的策略
        if results:
            best_result = max(results, key=lambda x: x['count'])
            self.logger.info(f"最终选择 {best_result['strategy']} 策略的结果")
            return best_result
        else:
            self.logger.warning(f"{round_name} 所有搜索策略都没有找到相关文献")
            return {
                'strategy': 'none',
                'query': '',
                'results': [],
                'count': 0,
                'search_input': user_input
            }
    
    def build_restructure_prompt(self, original_input: str) -> str:
        """构建查询重构的prompt"""
        return f"""
# 角色设定
你是一个专业的学术搜索查询优化助手，专门将过于具体的研究主题重构为更广泛但仍相关的搜索词。

# 任务目标
用户的原始查询可能过于具体或组合了太多限制条件，导致找不到相关文献。请提供3种重构策略的查询词。

# 重构策略
**策略1 - 简化组合**: 保留核心概念，去掉过度细节
**策略2 - 单一领域**: 只保留最主要的一个研究领域  
**策略3 - 相关技术**: 使用相关但更通用的技术词汇

# 重构示例
原始查询: "深度学习用于单细胞RNA测序数据的时间序列分析"
策略1: "深度学习单细胞分析"
策略2: "单细胞RNA测序"  
策略3: "机器学习生物信息学"

原始查询: "基于Transformer的多模态医学图像诊断系统"  
策略1: "Transformer医学图像"
策略2: "医学图像诊断"
策略3: "深度学习医学影像"

原始查询: "大模型在单细胞RNA测序数据时间序列分析中的应用"
策略1: "大模型单细胞分析"
策略2: "单细胞时间序列"
策略3: "机器学习基因组学"

# 输出格式
请严格按照以下格式输出，用"|"分隔：
策略1|策略2|策略3

# 实际任务
原始查询: {original_input}
输出:"""

    def restructure_query(self, original_input: str) -> list:
        """重构查询：生成多个重构策略的查询词"""
        prompt = self.build_restructure_prompt(original_input)
        self.logger.info(f"正在重构查询: '{original_input}'...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.3,
            )
            
            restructured_text = response.choices[0].message.content.strip()
            self.logger.info(f"重构响应: {restructured_text}")
            
            # 解析多个策略
            if "|" in restructured_text:
                strategies = [s.strip() for s in restructured_text.split("|")]
                # 确保有3个策略，如果不够就用原查询填充
                while len(strategies) < 3:
                    strategies.append(original_input)
                self.logger.info(f"解析到的重构策略: {strategies}")
                return strategies[:3]  # 只取前3个
            else:
                # 如果解析失败，返回原查询
                self.logger.warning("重构格式解析失败，使用原查询")
                return [original_input]
                
        except Exception as e:
            self.logger.error(f"查询重构失败: {e}")
            return [original_input]
    
    