#!/usr/bin/env python3
"""
Ultra Stable Website Visitor for Termux
No Crash - Unlimited Running
"""

import threading
import time
import random
import asyncio
import aiohttp
import ssl
from datetime import datetime
import os
import sys

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class StableVisitor:
    def __init__(self, url, target_rps=500):
        self.url = url
        self.target_rps = target_rps
        self.total_requests = 0
        self.successful = 0
        self.failed = 0
        self.running = True
        self.lock = threading.Lock()
        self.start_time = None
        
        # Termux-safe limits (কম থ্রেড কিন্তু stable)
        self.thread_count = min(50, int(target_rps / 10) + 5)
        if self.thread_count < 5:
            self.thread_count = 5
        if self.thread_count > 80:
            self.thread_count = 80
            
        # User agents
        self.user_agents = [
            'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120.0.6099.210',
            'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 Firefox/121.0',
            'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 Edge/120.0.0.0',
            'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/119.0.6045.163',
        ]
        
        print(f"{Colors.CYAN}[+] Termux Optimized Mode{Colors.RESET}")
        print(f"{Colors.CYAN}[+] Using {self.thread_count} threads (stable){Colors.RESET}")
    
    async def make_request_async(self, session, headers):
        """Single async request"""
        try:
            async with session.get(self.url, headers=headers, timeout=5, ssl=False) as response:
                with self.lock:
                    self.total_requests += 1
                    if response.status in [200, 301, 302, 304]:
                        self.successful += 1
                    else:
                        self.failed += 1
                return True
        except Exception:
            with self.lock:
                self.total_requests += 1
                self.failed += 1
            return False
    
    async def worker_async(self, worker_id):
        """Async worker that runs continuously"""
        connector = aiohttp.TCPConnector(limit=20, ssl=False)
        timeout = aiohttp.ClientTimeout(total=5)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            while self.running:
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                }
                
                await self.make_request_async(session, headers)
                
                # Rate limiting per thread
                if self.target_rps > 0:
                    await asyncio.sleep(1 / (self.target_rps / self.thread_count))
    
    def stats_updater(self):
        """Real-time statistics"""
        last_total = 0
        while self.running:
            time.sleep(1)
            if not self.running:
                break
            
            with self.lock:
                current_total = self.total_requests
                current_success = self.successful
                current_failed = self.failed
            
            rps = current_total - last_total
            last_total = current_total
            
            elapsed = time.time() - self.start_time
            avg_rps = current_total / elapsed if elapsed > 0 else 0
            
            # Progress bar
            bar_length = 40
            progress = min(1.0, rps / max(1, self.target_rps))
            filled = int(bar_length * progress)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            print(f"\r{Colors.CYAN}[{datetime.now().strftime('%H:%M:%S')}] "
                  f"[{bar}] {Colors.GREEN}{rps}{Colors.RESET}/{self.target_rps} RPS | "
                  f"Total: {Colors.WHITE}{current_total:>6}{Colors.RESET} | "
                  f"✓ {Colors.GREEN}{current_success:>6}{Colors.RESET} | "
                  f"✗ {Colors.RED}{current_failed:>5}{Colors.RESET} | "
                  f"Avg: {avg_rps:.0f}/s{Colors.RESET}", end="", flush=True)
    
    def start(self):
        """Main start function"""
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}")
        print("╔════════════════════════════════════════════════════╗")
        print("║     TERMUX STABLE VISITOR - NEVER CRASH           ║")
        print("║          Unlimited Mode - Runs Forever            ║")
        print("╚════════════════════════════════════════════════════╝")
        print(f"{Colors.RESET}")
        
        print(f"{Colors.YELLOW}[+] Target: {self.url}{Colors.RESET}")
        print(f"{Colors.YELLOW}[+] Target RPS: {self.target_rps}{Colors.RESET}")
        print(f"{Colors.YELLOW}[+] Threads: {self.thread_count}{Colors.RESET}")
        print(f"{Colors.GREEN}[+] Running... Press Ctrl+C to stop{Colors.RESET}\n")
        
        self.start_time = time.time()
        self.running = True
        
        # Start stats thread
        stats_thread = threading.Thread(target=self.stats_updater, daemon=True)
        stats_thread.start()
        
        # Start async workers
        try:
            asyncio.run(self.run_workers())
        except KeyboardInterrupt:
            self.stop()
    
    async def run_workers(self):
        """Run multiple async workers"""
        tasks = []
        for i in range(self.thread_count):
            task = asyncio.create_task(self.worker_async(i))
            tasks.append(task)
        
        # Run until stopped
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass
    
    def stop(self):
        """Stop gracefully"""
        self.running = False
        time.sleep(2)
        
        elapsed = time.time() - self.start_time
        
        print(f"\n\n{Colors.CYAN}{'='*55}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}          FINAL REPORT{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*55}{Colors.RESET}")
        print(f"{Colors.WHITE}Duration: {elapsed:.1f} seconds{Colors.RESET}")
        print(f"{Colors.WHITE}Total: {self.total_requests:,}{Colors.RESET}")
        print(f"{Colors.GREEN}Success: {self.successful:,}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed:,}{Colors.RESET}")
        
        if elapsed > 0:
            avg_rps = self.total_requests / elapsed
            print(f"{Colors.CYAN}Average RPS: {avg_rps:.1f}{Colors.RESET}")
        
        success_rate = (self.successful / self.total_requests * 100) if self.total_requests > 0 else 0
        print(f"{Colors.CYAN}Success Rate: {success_rate:.1f}%{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*55}{Colors.RESET}\n")

def main():
    """Main function"""
    os.system('clear')
    
    banner = f"""
{Colors.MAGENTA}{Colors.BOLD}
╔════════════════════════════════════════════════════╗
║         TERMUX STABLE WEBSITE VISITOR              ║
║              NO CRASH - UNLIMITED                  ║
║           Runs until you press Ctrl+C              ║
╚════════════════════════════════════════════════════╝
{Colors.RESET}
    """
    print(banner)
    
    # Get URL
    url = input(f"{Colors.GREEN}[?] Target URL: {Colors.RESET}").strip()
    if not url:
        print(f"{Colors.RED}[!] URL required!{Colors.RESET}")
        return
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Get RPS (reduced for stability)
    print(f"\n{Colors.YELLOW}[!] Stable RPS range: 50-500 for Termux{Colors.RESET}")
    try:
        target_rps = int(input(f"{Colors.GREEN}[?] Requests per second (default 200): {Colors.RESET}") or "200")
        target_rps = max(20, min(800, target_rps))
    except:
        target_rps = 200
    
    # Legal warning
    print(f"\n{Colors.RED}{Colors.BOLD}⚠️  LEGAL WARNING ⚠️{Colors.RESET}")
    print(f"{Colors.RED}Only use on websites you OWN or have PERMISSION!{Colors.RESET}")
    
    confirm = input(f"\n{Colors.CYAN}[?] Continue? (yes/no): {Colors.RESET}").lower()
    if confirm != 'yes':
        print(f"{Colors.RED}[!] Aborted.{Colors.RESET}")
        return
    
    # Install aiohttp if missing
    try:
        import aiohttp
    except ImportError:
        print(f"{Colors.YELLOW}[!] Installing aiohttp...{Colors.RESET}")
        os.system('pip install aiohttp -q')
    
    # Start
    visitor = StableVisitor(url, target_rps)
    try:
        visitor.start()
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Try reducing RPS or check internet{Colors.RESET}")

if __name__ == "__main__":
    main()