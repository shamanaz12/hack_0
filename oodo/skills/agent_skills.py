"""
Agent Skills - All AI functionality implemented as reusable skills
Each skill is a self-contained AI-powered capability
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dotenv import load_dotenv
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent_skills.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AgentSkill:
    """Base class for all agent skills"""
    
    def __init__(self, name: str, description: str, category: str):
        self.name = name
        self.description = description
        self.category = category
        self.enabled = True
        self.execution_count = 0
        self.last_executed: Optional[datetime] = None
    
    def execute(self, **kwargs) -> Dict:
        """Execute the skill - override in subclasses"""
        raise NotImplementedError
    
    def get_info(self) -> Dict:
        """Get skill information"""
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'enabled': self.enabled,
            'execution_count': self.execution_count,
            'last_executed': self.last_executed.isoformat() if self.last_executed else None
        }


class ContentGenerationSkill(AgentSkill):
    """Skill for generating various types of content"""
    
    def __init__(self):
        super().__init__(
            name='content_generation',
            description='Generate content for social media, emails, blogs, and more',
            category='content'
        )
        self.api_key = os.getenv('DASHSCOPE_API_KEY', '')
    
    def execute(self, content_type: str, topic: str, tone: str = 'professional',
                length: str = 'medium', keywords: List[str] = None,
                context: str = None) -> Dict:
        """Generate content based on parameters"""
        self.execution_count += 1
        self.last_executed = datetime.now()
        
        try:
            # Build prompt
            prompt = self._build_prompt(content_type, topic, tone, length, keywords, context)
            
            # Call AI API (using dashscope for Qwen)
            if self.api_key:
                result = self._call_ai_api(prompt)
            else:
                result = self._generate_fallback_content(content_type, topic, tone)
            
            logger.info(f"Content generated: type={content_type}, topic={topic[:50]}")
            
            return {
                'success': True,
                'content': result,
                'content_type': content_type,
                'topic': topic,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Content generation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _build_prompt(self, content_type: str, topic: str, tone: str,
                      length: str, keywords: List[str], context: str) -> str:
        """Build AI prompt for content generation"""
        length_map = {'short': '100-200 words', 'medium': '300-500 words', 'long': '600-1000 words'}
        
        prompt = f"""Generate {content_type} content about: {topic}

Requirements:
- Tone: {tone}
- Length: {length_map.get(length, '300-500 words')}
"""
        
        if keywords:
            prompt += f"- Include keywords: {', '.join(keywords)}\n"
        
        if context:
            prompt += f"- Context: {context}\n"
        
        prompt += "\nGenerate engaging, professional content:"
        
        return prompt
    
    def _call_ai_api(self, prompt: str) -> str:
        """Call Qwen AI API"""
        try:
            import dashscope
            from dashscope import Generation
            
            response = Generation.call(
                model='qwen-turbo',
                api_key=self.api_key,
                prompt=prompt
            )
            
            if response.status_code == 200:
                return response.output.text
            else:
                logger.warning(f"AI API error: {response.code}")
                return self._generate_fallback_content_from_prompt(prompt)
        except Exception as e:
            logger.error(f"AI API call error: {str(e)}")
            return self._generate_fallback_content_from_prompt(prompt)
    
    def _generate_fallback_content(self, content_type: str, topic: str, tone: str) -> str:
        """Generate fallback content when AI is unavailable"""
        templates = {
            'social_post': f"🚀 {topic}\n\nDiscover more about this exciting topic! #trending #innovation",
            'email': f"Subject: {topic}\n\nDear Recipient,\n\nI hope this email finds you well. I wanted to share information about {topic}.\n\nBest regards,",
            'blog_intro': f"# {topic}\n\nIn today's rapidly evolving landscape, {topic} has become increasingly important...",
            'product_description': f"Introducing our latest solution for {topic}. Designed with you in mind, this product delivers exceptional value..."
        }
        
        return templates.get(content_type, f"Content about {topic} in {tone} tone.")
    
    def _generate_fallback_content_from_prompt(self, prompt: str) -> str:
        """Generate simple fallback based on prompt"""
        return f"[AI Content] Based on your request: {prompt[:100]}..."


class DataAnalysisSkill(AgentSkill):
    """Skill for analyzing data and generating insights"""
    
    def __init__(self):
        super().__init__(
            name='data_analysis',
            description='Analyze data and generate actionable insights',
            category='analytics'
        )
    
    def execute(self, data: List[Dict], analysis_type: str = 'summary',
                focus_areas: List[str] = None) -> Dict:
        """Analyze data and provide insights"""
        self.execution_count += 1
        self.last_executed = datetime.now()
        
        try:
            if analysis_type == 'summary':
                result = self._analyze_summary(data)
            elif analysis_type == 'trends':
                result = self._analyze_trends(data)
            elif analysis_type == 'anomalies':
                result = self._analyze_anomalies(data)
            else:
                result = self._analyze_summary(data)
            
            if focus_areas:
                result = self._filter_by_focus(result, focus_areas)
            
            logger.info(f"Data analysis completed: type={analysis_type}")
            
            return {
                'success': True,
                'analysis': result,
                'analysis_type': analysis_type,
                'data_points': len(data),
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Data analysis error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_summary(self, data: List[Dict]) -> Dict:
        """Generate summary statistics"""
        if not data:
            return {'message': 'No data to analyze'}
        
        # Get numeric fields
        numeric_fields = []
        for key, value in data[0].items():
            if isinstance(value, (int, float)):
                numeric_fields.append(key)
        
        summary = {}
        for field in numeric_fields:
            values = [d.get(field, 0) for d in data if field in d]
            if values:
                summary[field] = {
                    'count': len(values),
                    'sum': sum(values),
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }
        
        return {
            'total_records': len(data),
            'numeric_fields': numeric_fields,
            'statistics': summary
        }
    
    def _analyze_trends(self, data: List[Dict]) -> Dict:
        """Analyze trends in data"""
        # Simple trend analysis
        if len(data) < 2:
            return {'message': 'Insufficient data for trend analysis'}
        
        return {
            'trend_direction': 'increasing' if data[-1] > data[0] else 'decreasing',
            'data_points': len(data),
            'change_percent': ((data[-1] - data[0]) / data[0] * 100) if data[0] != 0 else 0
        }
    
    def _analyze_anomalies(self, data: List[Dict]) -> Dict:
        """Detect anomalies in data"""
        if not data:
            return {'anomalies': []}
        
        # Simple anomaly detection using standard deviation
        numeric_values = []
        for d in data:
            for v in d.values():
                if isinstance(v, (int, float)):
                    numeric_values.append(v)
        
        if not numeric_values:
            return {'anomalies': []}
        
        avg = sum(numeric_values) / len(numeric_values)
        std_dev = (sum((x - avg) ** 2 for x in numeric_values) / len(numeric_values)) ** 0.5
        
        anomalies = [v for v in numeric_values if abs(v - avg) > 2 * std_dev]
        
        return {
            'average': avg,
            'std_deviation': std_dev,
            'anomalies': anomalies,
            'anomaly_count': len(anomalies)
        }
    
    def _filter_by_focus(self, result: Dict, focus_areas: List[str]) -> Dict:
        """Filter analysis results by focus areas"""
        filtered = {}
        for area in focus_areas:
            if area in result:
                filtered[area] = result[area]
        return filtered


class DecisionMakingSkill(AgentSkill):
    """Skill for making recommendations and decisions"""
    
    def __init__(self):
        super().__init__(
            name='decision_making',
            description='Make data-driven recommendations and decisions',
            category='decision'
        )
    
    def execute(self, context: str, options: List[Dict], 
                criteria: List[str] = None) -> Dict:
        """Make a decision based on context and options"""
        self.execution_count += 1
        self.last_executed = datetime.now()
        
        try:
            # Evaluate options
            evaluated_options = []
            for option in options:
                score = self._evaluate_option(option, criteria)
                evaluated_options.append({**option, 'score': score})
            
            # Sort by score
            evaluated_options.sort(key=lambda x: x['score'], reverse=True)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                context, evaluated_options, criteria
            )
            
            logger.info(f"Decision made: {len(options)} options evaluated")
            
            return {
                'success': True,
                'recommendation': recommendation,
                'ranked_options': evaluated_options,
                'best_option': evaluated_options[0] if evaluated_options else None,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Decision making error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _evaluate_option(self, option: Dict, criteria: List[str] = None) -> float:
        """Evaluate an option against criteria"""
        if not criteria:
            # Default scoring based on common fields
            score = 0
            if 'cost' in option:
                score += max(0, 100 - option['cost'])
            if 'benefit' in option:
                score += option['benefit'] * 10
            if 'risk' in option:
                score -= option['risk'] * 5
            if 'priority' in option:
                score += option['priority'] * 20
            return score
        
        # Score based on criteria
        score = 0
        for criterion in criteria:
            if criterion in option:
                value = option[criterion]
                if isinstance(value, (int, float)):
                    score += value
                elif isinstance(value, bool):
                    score += 50 if value else 0
                elif isinstance(value, str):
                    score += len(value)  # Simple string scoring
        
        return score
    
    def _generate_recommendation(self, context: str, options: List[Dict],
                                  criteria: List[str] = None) -> str:
        """Generate recommendation text"""
        if not options:
            return "No options available for recommendation."
        
        best = options[0]
        
        rec = f"Based on the analysis of {len(options)} options"
        if criteria:
            rec += f" using criteria: {', '.join(criteria)}"
        rec += f", we recommend: {best.get('name', 'Option 1')}."
        rec += f" This option scored {best.get('score', 0):.2f} points."
        
        return rec


class CommunicationSkill(AgentSkill):
    """Skill for handling communications"""
    
    def __init__(self):
        super().__init__(
            name='communication',
            description='Handle email drafting, response generation, and messaging',
            category='communication'
        )
    
    def execute(self, communication_type: str, recipient: str = None,
                subject: str = None, context: str = None,
                tone: str = 'professional') -> Dict:
        """Generate communication content"""
        self.execution_count += 1
        self.last_executed = datetime.now()
        
        try:
            if communication_type == 'email':
                content = self._generate_email(recipient, subject, context, tone)
            elif communication_type == 'response':
                content = self._generate_response(context, tone)
            elif communication_type == 'message':
                content = self._generate_message(context, tone)
            else:
                content = self._generate_message(context, tone)
            
            logger.info(f"Communication generated: type={communication_type}")
            
            return {
                'success': True,
                'content': content,
                'communication_type': communication_type,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Communication skill error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_email(self, recipient: str, subject: str, 
                        context: str, tone: str) -> Dict:
        """Generate email content"""
        greetings = {
            'professional': 'Dear',
            'friendly': 'Hello',
            'casual': 'Hi'
        }
        
        closings = {
            'professional': 'Best regards',
            'friendly': 'Warm regards',
            'casual': 'Cheers'
        }
        
        greeting = greetings.get(tone, 'Dear')
        closing = closings.get(tone, 'Best regards')
        
        body = context or "I hope this email finds you well."
        
        return {
            'recipient': recipient or '[Recipient]',
            'subject': subject or '[Subject]',
            'greeting': f"{greeting} {recipient or '[Recipient]}',",
            'body': body,
            'closing': f"{closing},",
            'signature': '[Your Name]'
        }
    
    def _generate_response(self, context: str, tone: str) -> str:
        """Generate response to a message"""
        responses = {
            'professional': "Thank you for your message. I appreciate you reaching out.",
            'friendly': "Thanks for getting in touch! Great to hear from you.",
            'casual': "Hey, thanks for the message!"
        }
        
        return responses.get(tone, responses['professional']) + f"\n\n{context or ''}"
    
    def _generate_message(self, context: str, tone: str) -> str:
        """Generate a short message"""
        return context or "Hello! This is an automated message."


class SchedulingSkill(AgentSkill):
    """Skill for scheduling and calendar management"""
    
    def __init__(self):
        super().__init__(
            name='scheduling',
            description='Schedule meetings, manage calendars, and set reminders',
            category='productivity'
        )
    
    def execute(self, action: str, title: str = None, 
                start_time: datetime = None, end_time: datetime = None,
                attendees: List[str] = None, location: str = None) -> Dict:
        """Execute scheduling action"""
        self.execution_count += 1
        self.last_executed = datetime.now()
        
        try:
            if action == 'schedule_meeting':
                result = self._schedule_meeting(title, start_time, end_time, attendees, location)
            elif action == 'set_reminder':
                result = self._set_reminder(title, start_time)
            elif action == 'check_availability':
                result = self._check_availability(start_time, end_time, attendees)
            else:
                result = {'error': f'Unknown action: {action}'}
            
            logger.info(f"Scheduling action completed: {action}")
            
            return {
                'success': True,
                'action': action,
                'result': result,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Scheduling skill error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _schedule_meeting(self, title: str, start_time: datetime,
                          end_time: datetime, attendees: List[str],
                          location: str) -> Dict:
        """Schedule a meeting"""
        return {
            'meeting_id': f"MTG_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'title': title or 'Untitled Meeting',
            'start_time': start_time.isoformat() if start_time else None,
            'end_time': end_time.isoformat() if end_time else None,
            'attendees': attendees or [],
            'location': location or 'TBD',
            'status': 'scheduled'
        }
    
    def _set_reminder(self, title: str, reminder_time: datetime) -> Dict:
        """Set a reminder"""
        return {
            'reminder_id': f"REM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'title': title,
            'reminder_time': reminder_time.isoformat() if reminder_time else None,
            'status': 'active'
        }
    
    def _check_availability(self, start_time: datetime, end_time: datetime,
                            attendees: List[str]) -> Dict:
        """Check availability (simplified)"""
        return {
            'available': True,
            'start_time': start_time.isoformat() if start_time else None,
            'end_time': end_time.isoformat() if end_time else None,
            'attendees_status': {a: 'available' for a in (attendees or [])}
        }


class ResearchSkill(AgentSkill):
    """Skill for research and information gathering"""
    
    def __init__(self):
        super().__init__(
            name='research',
            description='Gather and synthesize information on topics',
            category='research'
        )
    
    def execute(self, topic: str, sources: List[str] = None,
                depth: str = 'medium') -> Dict:
        """Conduct research on a topic"""
        self.execution_count += 1
        self.last_executed = datetime.now()
        
        try:
            # Simulated research (in production, this would call search APIs)
            research_result = self._conduct_research(topic, sources, depth)
            
            logger.info(f"Research completed: topic={topic[:50]}")
            
            return {
                'success': True,
                'topic': topic,
                'research': research_result,
                'depth': depth,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Research skill error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _conduct_research(self, topic: str, sources: List[str], 
                          depth: str) -> Dict:
        """Conduct research (simplified)"""
        depth_pages = {'shallow': 1, 'medium': 3, 'deep': 5}
        pages = depth_pages.get(depth, 3)
        
        return {
            'summary': f"Research summary for: {topic}",
            'key_points': [
                f"Key point 1 about {topic}",
                f"Key point 2 about {topic}",
                f"Key point 3 about {topic}"
            ],
            'sources_used': sources or ['General knowledge'],
            'pages_analyzed': pages,
            'confidence': 0.85
        }


class SkillManager:
    """Manager for all agent skills"""
    
    def __init__(self):
        self.skills: Dict[str, AgentSkill] = {}
        self._register_default_skills()
        logger.info("Skill Manager initialized")
    
    def _register_default_skills(self):
        """Register default skills"""
        skills = [
            ContentGenerationSkill(),
            DataAnalysisSkill(),
            DecisionMakingSkill(),
            CommunicationSkill(),
            SchedulingSkill(),
            ResearchSkill()
        ]
        
        for skill in skills:
            self.skills[skill.name] = skill
    
    def get_skill(self, name: str) -> Optional[AgentSkill]:
        """Get a skill by name"""
        return self.skills.get(name)
    
    def execute_skill(self, name: str, **kwargs) -> Dict:
        """Execute a skill by name"""
        skill = self.get_skill(name)
        if not skill:
            return {'success': False, 'error': f'Skill not found: {name}'}
        
        if not skill.enabled:
            return {'success': False, 'error': f'Skill disabled: {name}'}
        
        return skill.execute(**kwargs)
    
    def get_all_skills(self) -> List[Dict]:
        """Get information about all skills"""
        return [skill.get_info() for skill in self.skills.values()]
    
    def get_skills_by_category(self, category: str) -> List[Dict]:
        """Get skills by category"""
        return [
            skill.get_info() 
            for skill in self.skills.values() 
            if skill.category == category
        ]
    
    def enable_skill(self, name: str):
        """Enable a skill"""
        if name in self.skills:
            self.skills[name].enabled = True
            logger.info(f"Skill enabled: {name}")
    
    def disable_skill(self, name: str):
        """Disable a skill"""
        if name in self.skills:
            self.skills[name].enabled = False
            logger.info(f"Skill disabled: {name}")


# Global skill manager instance
skill_manager = SkillManager()


if __name__ == '__main__':
    print("Agent Skills System")
    print("=" * 50)
    
    # List all skills
    print("\nAvailable Skills:")
    for skill in skill_manager.get_all_skills():
        print(f"  - {skill['name']} ({skill['category']}): {skill['description']}")
    
    # Test content generation
    print("\n\nTesting Content Generation Skill:")
    result = skill_manager.execute_skill(
        'content_generation',
        content_type='social_post',
        topic='AI in Business',
        tone='professional',
        keywords=['automation', 'efficiency', 'growth']
    )
    print(json.dumps(result, indent=2))
    
    # Test data analysis
    print("\n\nTesting Data Analysis Skill:")
    test_data = [
        {'revenue': 1000, 'cost': 500},
        {'revenue': 1500, 'cost': 600},
        {'revenue': 2000, 'cost': 700}
    ]
    result = skill_manager.execute_skill(
        'data_analysis',
        data=test_data,
        analysis_type='summary'
    )
    print(json.dumps(result, indent=2))
    
    # Test communication
    print("\n\nTesting Communication Skill:")
    result = skill_manager.execute_skill(
        'communication',
        communication_type='email',
        recipient='John Doe',
        subject='Meeting Request',
        context='I would like to schedule a meeting to discuss the project.',
        tone='professional'
    )
    print(json.dumps(result, indent=2))
