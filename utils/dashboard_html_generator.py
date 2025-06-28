import json
import logging
from pathlib import Path
from .dashboard_data_export import DashboardDataExporter

class DashboardHTMLGenerator:
    """Generate complete HTML dashboard with embedded data"""
    
    def __init__(self, tumorboard_base_path=None):
        self.tumorboard_base_path = tumorboard_base_path
        self.exporter = DashboardDataExporter(tumorboard_base_path)
    
    def generate_complete_html(self, output_path=None, interactive=True):
        """Generate complete HTML file with embedded JSON data"""
        if output_path is None:
            # Use tumorboard base path if available, otherwise fall back to user home
            if self.tumorboard_base_path is not None:
                output_path = self.tumorboard_base_path / "__SQLite_database" / "dashboard" / "dashboard.html"
            else:
                output_path = Path.home() / "tumorboards" / "__SQLite_database" / "dashboard" / "dashboard.html"
        
        try:
            # Get dashboard data
            dashboard_data = self._get_dashboard_data()
            if not dashboard_data:
                return None
            
            # Choose template based on interactive flag
            template_name = "dashboard_interactive.html" if interactive else "dashboard_simple.html"
            template_path = Path(__file__).parent.parent / "templates" / template_name
            
            if not template_path.exists():
                logging.error(f"Template not found: {template_path}")
                return None
            
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Embed JSON data directly in HTML
            json_data = json.dumps(dashboard_data, ensure_ascii=False, indent=2)
            
            # Replace the fetch call with embedded data
            old_script = """        // Load dashboard data (embedded)
        async function loadDashboardData() {
            try {
                // Use embedded data instead of fetch
                dashboardData = {"""
            
            new_script = f"""        // Load dashboard data (embedded)
        async function loadDashboardData() {{
            try {{
                // Use embedded data instead of fetch
                dashboardData = {json_data};"""
            
            # Find and replace the data placeholder
            if old_script in html_content:
                # Find the end of the existing data object
                start_pos = html_content.find(old_script) + len(old_script)
                end_pos = html_content.find('};', start_pos) + 1
                
                # Replace the entire data section
                html_content = (html_content[:html_content.find(old_script)] + 
                              new_script + 
                              html_content[end_pos:])
            else:
                logging.warning("Could not find data placeholder in template")
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write complete HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logging.info(f"Complete dashboard HTML generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logging.error(f"Error generating dashboard HTML: {e}")
            return None
    
    def _get_dashboard_data(self):
        """Get dashboard data as dictionary"""
        try:
            # Export to temporary location and read back
            if self.tumorboard_base_path is not None:
                temp_path = self.tumorboard_base_path / "__SQLite_database" / "temp_dashboard_data.json"
            else:
                temp_path = Path.home() / "tumorboards" / "__SQLite_database" / "temp_dashboard_data.json"
            export_path = self.exporter.export_dashboard_data(temp_path)
            
            if not export_path or not Path(export_path).exists():
                return None
            
            with open(export_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clean up temp file
            Path(export_path).unlink(missing_ok=True)
            
            return data
            
        except Exception as e:
            logging.error(f"Error getting dashboard data: {e}")
            return None


def generate_complete_dashboard(interactive=True, tumorboard_base_path=None):
    """Generate complete dashboard HTML with embedded data"""
    # Determine correct tumorboard base path if not provided
    if tumorboard_base_path is None:
        # Try K: first, fall back to user home
        k_path = Path("K:/RAO_Projekte/App/tumorboards")
        if k_path.exists() and k_path.is_dir():
            tumorboard_base_path = k_path
        else:
            tumorboard_base_path = Path.home() / "tumorboards"
    
    generator = DashboardHTMLGenerator(tumorboard_base_path)
    return generator.generate_complete_html(interactive=interactive) 