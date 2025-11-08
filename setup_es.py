#!/usr/bin/env python3
"""
Script to test and configure Elasticsearch connection
"""
import getpass
from elasticsearch import Elasticsearch

def test_connection(url, username, password):
    """Test Elasticsearch connection"""
    try:
        if password:
            es = Elasticsearch(
                [url],
                basic_auth=(username, password),
                verify_certs=False,
                ssl_show_warn=False
            )
        else:
            es = Elasticsearch([url])
        
        info = es.info()
        print(f"\n✅ SUCCESS! Connected to Elasticsearch")
        print(f"Cluster: {info['cluster_name']}")
        print(f"Version: {info['version']['number']}")
        return True, password
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False, None

def main():
    print("="*60)
    print("Elasticsearch Connection Setup")
    print("="*60)
    
    url = input("\nElasticsearch URL [http://localhost:9200]: ").strip() or "http://localhost:9200"
    username = input("Username [elastic]: ").strip() or "elastic"
    
    print("\nTrying without password...")
    success, _ = test_connection(url, username, "")
    
    if not success:
        print("\nAuthentication required. Please enter password:")
        password = getpass.getpass("Password: ")
        success, pwd = test_connection(url, username, password)
        
        if success:
            # Update config file
            config_path = "src/config.py"
            with open(config_path, 'r') as f:
                content = f.read()
            
            content = content.replace(
                "password = 'changeme'",
                f"password = '{password}'"
            )
            
            with open(config_path, 'w') as f:
                f.write(content)
            
            print(f"\n✅ Configuration updated in {config_path}")
            print("\nYou can now run: ./run_app.sh")
        else:
            print("\n❌ Could not connect. Please check your credentials.")
            print("\nTo reset password:")
            print("docker exec -it $(docker ps -q) bin/elasticsearch-reset-password -u elastic -i")
    else:
        print("\n✅ No authentication needed. Your system is ready!")

if __name__ == "__main__":
    main()
