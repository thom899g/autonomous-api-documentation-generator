import logging
from typing import Dict, Any
from .analyser import CodeAnalyser

logger = logging.getLogger(__name__)

class APIMonitor:
    """
    Monitor API usage and update documentation in real-time.

    This class tracks API calls and updates the documentation based on usage patterns.
    It handles edge cases such as unexpected API outages and request spikes.
    """

    def __init__(self, analyser: CodeAnalyser):
        """
        Initialize the APIMonitor with a CodeAnalyser instance.

        Args:
            analyser: Instance of CodeAnalyser to use for documentation generation.
        """
        self.analyser = analyser
        logging.basicConfig(
            filename='api_monitor.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def monitor_api_usage(self, api_endpoints: Dict[str, str]) -> None:
        """
        Monitor API usage and update documentation.

        Args:
            api_endpoints: Dictionary mapping endpoint names to URLs.
        """
        last_updated = {}
        
        while True:
            for endpoint_name, endpoint_url in api_endpoints.items():
                try:
                    response = self._make_request(endpoint_url)
                    
                    if not response.ok:
                        logger.error(f"Failed request to {endpoint_url}: {response.status_code}")
                        continue

                    usage_data = response.json()
                    
                    # Generate documentation based on usage data
                    self._update_documentation(
                        endpoint_name,
                        usage_data
                    )
                    
                    last_updated[endpoint_name] = time.time()

                except Exception as e:
                    logger.error(f"Error monitoring {endpoint_name}: {str(e)}")
                    continue

            time.sleep(60)  # Check every minute

    def _make_request(self,