"""
Intelligent Real Estate Agent
A true AI agent that uses LLM-based understanding instead of regex patterns
"""

import json
import re
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    """Structured response from the AI agent"""
    intent: str
    confidence: float
    entities: Dict[str, Any]
    plan: List[str]
    response: Dict[str, Any]
    reasoning: str

class IntelligentRealEstateAgent:
    """
    A true AI agent that understands natural language and plans actions dynamically
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.1:8b"  # Using a capable model
        self.conversation_memory = []
        self.user_preferences = {}
        
    async def understand_query(self, query: str) -> AgentResponse:
        """
        Use LLM to understand the user's intent and extract entities
        """
        system_prompt = """You are an intelligent real estate agent. Analyze the user's query and provide a structured response.

Return a JSON response with:
{
    "intent": "search_properties|compare_locations|price_analysis|affordability_calculation|how_to_guide|market_insights",
    "confidence": 0.0-1.0,
    "entities": {
        "locations": ["location1", "location2"],
        "property_types": ["villa", "apartment"],
        "price_range": {"min": 0, "max": 0},
        "keywords": ["keyword1", "keyword2"],
        "comparison_type": "price|features|market"
    },
    "plan": ["step1", "step2", "step3"],
    "reasoning": "explanation of your analysis"
}

Examples:
- "Compare prices in Palm Jumeirah vs Dubai Marina" -> intent: "compare_locations", entities: {"locations": ["Palm Jumeirah", "Dubai Marina"], "comparison_type": "price"}
- "How many years to buy a villa in Victory Heights" -> intent: "affordability_calculation", entities: {"locations": ["Victory Heights"], "property_types": ["villa"]}
- "Show me all villas in Damac Hills" -> intent: "search_properties", entities: {"locations": ["Damac Hills"], "property_types": ["villa"]}
"""

        user_prompt = f"Analyze this real estate query: '{query}'"
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "stream": False,
                    "format": "json"
                }
                
                async with session.post(f"{self.ollama_url}/api/chat", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("message", {}).get("content", "{}")
                        
                        try:
                            parsed = json.loads(content)
                            return AgentResponse(
                                intent=parsed.get("intent", "search_properties"),
                                confidence=parsed.get("confidence", 0.8),
                                entities=parsed.get("entities", {}),
                                plan=parsed.get("plan", []),
                                response={},
                                reasoning=parsed.get("reasoning", "")
                            )
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse LLM response: {content}")
                            return self._fallback_understanding(query)
                    else:
                        logger.error(f"LLM API error: {response.status}")
                        return self._fallback_understanding(query)
                        
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return self._fallback_understanding(query)
    
    def _fallback_understanding(self, query: str) -> AgentResponse:
        """Fallback understanding when LLM is not available"""
        query_lower = query.lower()
        
        # Simple keyword-based fallback
        if any(word in query_lower for word in ["compare", "versus", "vs", "difference"]):
            intent = "compare_locations"
            entities = {"comparison_type": "price"}
        elif any(word in query_lower for word in ["years", "afford", "salary", "work"]):
            intent = "affordability_calculation"
            entities = {}
        elif any(word in query_lower for word in ["how to", "guide", "process"]):
            intent = "how_to_guide"
            entities = {}
        elif any(word in query_lower for word in ["average", "price", "market"]):
            intent = "price_analysis"
            entities = {}
        else:
            intent = "search_properties"
            entities = {}
        
        return AgentResponse(
            intent=intent,
            confidence=0.6,
            entities=entities,
            plan=[f"Execute {intent}"],
            response={},
            reasoning="Fallback keyword-based analysis"
        )
    
    async def execute_plan(self, agent_response: AgentResponse, query: str) -> Dict[str, Any]:
        """
        Execute the planned actions based on the agent's understanding
        """
        intent = agent_response.intent
        entities = agent_response.entities
        
        if intent == "compare_locations":
            return await self._compare_locations(entities, query)
        elif intent == "affordability_calculation":
            return await self._calculate_affordability(entities, query)
        elif intent == "price_analysis":
            return await self._analyze_prices(entities, query)
        elif intent == "how_to_guide":
            return await self._provide_guide(entities, query)
        elif intent == "market_insights":
            return await self._provide_market_insights(entities, query)
        else:  # search_properties
            return await self._search_properties(entities, query)
    
    async def _compare_locations(self, entities: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Compare two or more locations"""
        locations = entities.get("locations", [])
        comparison_type = entities.get("comparison_type", "price")
        
        # Always try to extract locations from query first (more reliable)
        extracted_locations = await self._extract_locations_from_query(query)
        if len(extracted_locations) >= 2:
            locations = extracted_locations
        elif len(locations) < 2:
            # Try to extract locations from query using LLM
            locations = await self._extract_locations_from_query(query)
        
        print(f"DEBUG: Extracted locations: {locations}")
        
        if len(locations) < 2:
            return {
                "error": "Could not identify two locations to compare",
                "suggestion": "Please specify two locations, e.g., 'Compare Palm Jumeirah vs Dubai Marina'",
                "debug_info": {
                    "query": query,
                    "entities": entities,
                    "extracted_locations": locations
                }
            }
        
        # Search properties for each location
        results = {}
        for location in locations[:2]:  # Limit to 2 locations
            try:
                import test_prop as tp
                search_filters = {"query": location}
                print(f"DEBUG: Searching for location '{location}' with filters: {search_filters}")
                props = tp.search_properties(search_filters)
                print(f"DEBUG: Found {len(props) if props else 0} properties for {location}")
                results[location] = props
            except Exception as e:
                logger.error(f"Error searching {location}: {e}")
                print(f"DEBUG: Error searching {location}: {e}")
                results[location] = []
        
        # Calculate comparison metrics
        comparison_data = {}
        for location, props in results.items():
            if props:
                prices = [p.get("price", 0) for p in props if p.get("price")]
                if prices:
                    comparison_data[location] = {
                        "count": len(props),
                        "avg_price": sum(prices) / len(prices),
                        "min_price": min(prices),
                        "max_price": max(prices)
                    }
                else:
                    comparison_data[location] = {"count": len(props), "avg_price": None}
            else:
                comparison_data[location] = {"count": 0, "avg_price": None}
        
        # Generate insights
        insights = []
        if len(comparison_data) == 2:
            loc1, loc2 = list(comparison_data.keys())
            data1, data2 = comparison_data[loc1], comparison_data[loc2]
            
            if data1.get("avg_price") and data2.get("avg_price"):
                diff = data1["avg_price"] - data2["avg_price"]
                diff_pct = (diff / data2["avg_price"]) * 100 if data2["avg_price"] > 0 else 0
                
                insights.append(f"{loc1} has an average price of AED {data1['avg_price']:,.0f} ({data1['count']} properties)")
                insights.append(f"{loc2} has an average price of AED {data2['avg_price']:,.0f} ({data2['count']} properties)")
                insights.append(f"Difference: AED {abs(diff):,.0f} ({abs(diff_pct):.1f}% {'higher' if diff > 0 else 'lower'} in {loc1})")
        
        return {
            "intent": "comparison",
            "comparison_data": comparison_data,
            "insights": insights,
            "all_properties": [prop for props in results.values() for prop in props]
        }
    
    async def _calculate_affordability(self, entities: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Calculate affordability based on property prices and income assumptions"""
        # Extract location and property type from entities or query
        location = entities.get("locations", ["Dubai"])[0] if entities.get("locations") else "Dubai"
        property_type = entities.get("property_types", ["villa"])[0] if entities.get("property_types") else "villa"
        
        # Search for properties
        try:
            import test_prop as tp
            search_filters = {"query": location, "property_type": property_type}
            props = tp.search_properties(search_filters)
        except Exception as e:
            logger.error(f"Error searching properties: {e}")
            props = []
        
        if not props:
            return {
                "error": f"No properties found for {property_type} in {location}",
                "suggestion": "Try a broader location search or different property type"
            }
        
        # Calculate average price
        prices = [p.get("price", 0) for p in props if p.get("price")]
        if not prices:
            return {
                "error": "No price information available for affordability calculation",
                "suggestion": "Try properties with listed prices"
            }
        
        avg_price = sum(prices) / len(prices)
        
        # Default assumptions (can be made configurable)
        annual_salary = 240000  # AED per year
        savings_rate = 0.20     # 20% of salary saved per year
        
        # Try to extract salary from query
        import re
        salary_match = re.search(r"with\s*(\d+k|\d+)\s*salary", query.lower())
        if salary_match:
            salary_str = salary_match.group(1)
            if 'k' in salary_str:
                annual_salary = int(float(salary_str.replace('k', '')) * 1000)
            else:
                annual_salary = int(salary_str)
        
        years_to_save = (avg_price / (annual_salary * savings_rate)) if (annual_salary * savings_rate) > 0 else float('inf')
        
        return {
            "intent": "affordability",
            "analysis": {
                "average_property_price": f"AED {avg_price:,.0f}",
                "assumed_annual_salary": f"AED {annual_salary:,.0f}",
                "assumed_savings_rate": f"{savings_rate*100:.0f}%",
                "years_to_save": f"{years_to_save:.1f} years" if years_to_save != float('inf') else "N/A"
            },
            "insights": [
                f"You would need approximately {years_to_save:.1f} years of work to save for an average {property_type} in {location}",
                f"Based on {len(props)} properties with an average price of AED {avg_price:,.0f}",
                f"Assuming an annual salary of AED {annual_salary:,.0f} and saving {savings_rate*100:.0f}% of it",
                "This is a simplified estimate and does not include down payments, mortgage interest, or other costs"
            ],
            "properties": props
        }
    
    async def _analyze_prices(self, entities: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Analyze price trends and statistics"""
        location = entities.get("locations", ["Dubai"])[0] if entities.get("locations") else "Dubai"
        
        try:
            import test_prop as tp
            search_filters = {"query": location}
            props = tp.search_properties(search_filters)
        except Exception as e:
            logger.error(f"Error searching properties: {e}")
            props = []
        
        if not props:
            return {
                "error": f"No properties found in {location}",
                "suggestion": "Try a broader location search"
            }
        
        prices = [p.get("price", 0) for p in props if p.get("price")]
        if not prices:
            return {
                "error": "No price information available",
                "suggestion": "Try properties with listed prices"
            }
        
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        return {
            "intent": "price_analysis",
            "analysis": {
                "average_price": f"AED {avg_price:,.0f}",
                "price_range": f"AED {min_price:,.0f} - AED {max_price:,.0f}",
                "property_count": len(props),
                "location": location
            },
            "insights": [
                f"Found {len(props)} properties in {location}",
                f"Average price: AED {avg_price:,.0f}",
                f"Price range: AED {min_price:,.0f} to AED {max_price:,.0f}",
                f"Price variation: {((max_price - min_price) / avg_price * 100):.1f}%"
            ],
            "properties": props
        }
    
    async def _provide_guide(self, entities: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Provide how-to guides for real estate processes"""
        location = entities.get("locations", ["Dubai"])[0] if entities.get("locations") else "Dubai"
        
        if "buy" in query.lower() or "purchase" in query.lower():
            return {
                "intent": "how_to_guide",
                "guide": {
                    "title": f"How to Buy Property in {location}",
                    "steps": [
                        "1. **Get Pre-Approval**: Contact a bank for mortgage pre-approval",
                        "2. **Find a Property**: Search for available properties in the area",
                        "3. **Make an Offer**: Work with a real estate agent to make an offer",
                        "4. **Legal Process**: Complete due diligence and legal documentation",
                        "5. **Final Payment**: Complete the transaction and transfer ownership"
                    ],
                    "additional_info": {
                        "location": location,
                        "note": "Process may vary based on property type and location"
                    }
                }
            }
        elif "sell" in query.lower():
            return {
                "intent": "how_to_guide",
                "guide": {
                    "title": f"How to Sell Property in {location}",
                    "steps": [
                        "1. **Property Valuation**: Get professional valuation",
                        "2. **Prepare Property**: Clean, stage, and make necessary repairs",
                        "3. **List Property**: Work with real estate agent to list",
                        "4. **Showings**: Schedule and conduct property viewings",
                        "5. **Negotiate & Close**: Handle offers and complete sale"
                    ]
                }
            }
        else:
            return {
                "intent": "how_to_guide",
                "guide": {
                    "title": "Real Estate Process Guide",
                    "steps": [
                        "1. **Define Your Needs**: Determine budget, location, and property type",
                        "2. **Research Market**: Understand current market conditions",
                        "3. **Get Professional Help**: Work with qualified real estate agents",
                        "4. **Due Diligence**: Verify all property details and legal status",
                        "5. **Complete Transaction**: Follow proper legal and financial procedures"
                    ]
                }
            }
    
    async def _provide_market_insights(self, entities: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Provide market insights and trends"""
        location = entities.get("locations", ["Dubai"])[0] if entities.get("locations") else "Dubai"
        
        try:
            import test_prop as tp
            search_filters = {"query": location}
            props = tp.search_properties(search_filters)
        except Exception as e:
            logger.error(f"Error searching properties: {e}")
            props = []
        
        if not props:
            return {
                "error": f"No market data available for {location}",
                "suggestion": "Try a broader location search"
            }
        
        # Analyze market data
        prices = [p.get("price", 0) for p in props if p.get("price")]
        property_types = [p.get("property_type", "unknown") for p in props]
        
        insights = [
            f"Market overview for {location}:",
            f"Total properties available: {len(props)}",
        ]
        
        if prices:
            avg_price = sum(prices) / len(prices)
            insights.append(f"Average price: AED {avg_price:,.0f}")
            insights.append(f"Price range: AED {min(prices):,.0f} - AED {max(prices):,.0f}")
        
        # Property type distribution
        type_counts = {}
        for prop_type in property_types:
            type_counts[prop_type] = type_counts.get(prop_type, 0) + 1
        
        if type_counts:
            insights.append("Property type distribution:")
            for prop_type, count in type_counts.items():
                insights.append(f"- {prop_type}: {count} properties")
        
        return {
            "intent": "market_insights",
            "insights": insights,
            "market_data": {
                "total_properties": len(props),
                "average_price": sum(prices) / len(prices) if prices else None,
                "property_types": type_counts
            },
            "properties": props
        }
    
    async def _search_properties(self, entities: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Search for properties based on criteria"""
        search_filters = {}
        
        # Always try to extract location from query first (more reliable)
        extracted_locations = await self._extract_locations_from_query(query)
        if extracted_locations:
            search_filters["query"] = extracted_locations[0]
            print(f"DEBUG: Using extracted location: {extracted_locations[0]}")
        elif entities.get("locations"):
            search_filters["query"] = entities["locations"][0]
            print(f"DEBUG: Using entity location: {entities['locations'][0]}")
        
        if entities.get("property_types"):
            search_filters["property_type"] = entities["property_types"][0]
        if entities.get("price_range"):
            price_range = entities["price_range"]
            if price_range.get("min"):
                search_filters["min_price"] = price_range["min"]
            if price_range.get("max"):
                search_filters["max_price"] = price_range["max"]
        
        print(f"DEBUG: Final search filters: {search_filters}")
        
        try:
            import test_prop as tp
            props = tp.search_properties(search_filters)
            print(f"DEBUG: Found {len(props) if props else 0} properties")
        except Exception as e:
            logger.error(f"Error searching properties: {e}")
            print(f"DEBUG: Error in search: {e}")
            props = []
        
        return {
            "intent": "search_properties",
            "properties": props,
            "count": len(props) if props else 0,
            "filters_used": search_filters
        }
    
    async def _extract_locations_from_query(self, query: str) -> List[str]:
        """Extract locations from query using regex patterns (more reliable than LLM)"""
        
        locations = []
        query_lower = query.lower()
        
        # Try to find locations using various patterns
        # Pattern 1: "X vs Y" or "X versus Y"
        vs_patterns = [
            r"([A-Za-z\s]+?)\s+(?:vs\.?|versus)\s+([A-Za-z\s]+?)(?:\?|$|\s+for|\s+properties)",
            r"compare\s+(?:prices?\s+in\s+)?([A-Za-z\s]+?)\s+(?:vs\.?|versus)\s+([A-Za-z\s]+?)(?:\?|$)",
            r"([A-Za-z\s]+?)\s+compared?\s+to\s+([A-Za-z\s]+?)(?:\?|$)",
            r"difference\s+between\s+([A-Za-z\s]+?)\s+and\s+([A-Za-z\s]+?)(?:\?|$)"
        ]
        
        for pattern in vs_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                loc1 = match.group(1).strip()
                loc2 = match.group(2).strip()
                
                # Clean up the locations
                loc1 = self._clean_location_name(loc1)
                loc2 = self._clean_location_name(loc2)
                
                # Return both locations as-is (let Property Finder API handle validation)
                return [loc1, loc2]
        
        # Pattern 2: Complex location extraction (e.g., "Carmen Villa in Victory Heights")
        complex_patterns = [
            r"in\s+([A-Za-z\s]+?)\s+in\s+([A-Za-z\s]+?)(?:\s+under|\s+with|\s+for|\s+between|$)",
            r"([A-Za-z\s]+?)\s+in\s+([A-Za-z\s]+?)(?:\s+under|\s+with|\s+for|\s+between|$)"
        ]
        
        for pattern in complex_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                # For "X in Y" patterns, Y is usually the main location
                location1 = match.group(1).strip()
                location2 = match.group(2).strip()
                
                # Clean both locations
                location1 = self._clean_location_name(location1)
                location2 = self._clean_location_name(location2)
                
                # Return the second location (usually the main area) - let Property Finder API validate
                return [location2]
        
        # Pattern 3: Single location extraction
        location_patterns = [
            r"in\s+([A-Za-z\s]+?)(?:\s+under|\s+with|\s+for|\s+between|$)",
            r"near\s+(?:the\s+)?([A-Za-z\s]+?)(?:\s+units?|\s+propert(?:y|ies)|\s+apart(?:ment)?s?|\s+villas?|\s+and|\s+but|\s*$)",
            r"around\s+(?:the\s+)?([A-Za-z\s]+?)(?:\s+units?|\s+propert(?:y|ies)|\s+apart(?:ment)?s?|\s+villas?|\s+and|\s+but|\s*$)",
            r"close to\s+(?:the\s+)?([A-Za-z\s]+?)(?:\s+units?|\s+propert(?:y|ies)|\s+apart(?:ment)?s?|\s+villas?|\s+and|\s+but|\s*$)"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                location = self._clean_location_name(location)
                # Return location as-is - let Property Finder API handle validation
                return [location]
        
        return []
    
    def _clean_location_name(self, location: str) -> str:
        """Clean and normalize location names"""
        # Remove common prefixes/suffixes
        location = re.sub(r"^(the|in|at|near|around|close to)\s+", "", location, flags=re.IGNORECASE)
        location = re.sub(r"\s+(properties|property|units|unit|apartments|apartment|villas|villa|for sale|for rent)$", "", location, flags=re.IGNORECASE)
        
        # Title case
        location = location.title()
        
        return location.strip()
    
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Main method to process a user query intelligently
        """
        # Store in conversation memory
        self.conversation_memory.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "type": "user"
        })
        
        # Understand the query
        agent_response = await self.understand_query(query)
        
        # Execute the plan
        result = await self.execute_plan(agent_response, query)
        
        # Store response in memory
        self.conversation_memory.append({
            "timestamp": datetime.now().isoformat(),
            "response": result,
            "type": "agent"
        })
        
        # Return structured response
        return {
            "success": True,
            "agent_id": "intelligent_real_estate_agent_v1",
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "understanding": {
                "intent": agent_response.intent,
                "confidence": agent_response.confidence,
                "entities": agent_response.entities,
                "reasoning": agent_response.reasoning
            },
            "result": result
        }

# Global agent instance
agent = IntelligentRealEstateAgent()
