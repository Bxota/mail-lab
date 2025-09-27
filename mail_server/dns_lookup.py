import dns.resolver

def print_mx(domain: str):
    print(f"\n🔎 MX for {domain}:")
    try:
        answers = dns.resolver.resolve(domain, "MX")
        for r in sorted(answers, key=lambda r: r.preference):
            print(f"  {r.preference}\t{r.exchange.to_text()}")
    except Exception as e:
        print("  (erreur MX)", e)

def print_txt(domain: str):
    print(f"\n🔎 TXT for {domain}:")
    try:
        answers = dns.resolver.resolve(domain, "TXT")
        for r in answers:
            # r.strings is deprecated in newer dnspython; decode parts manually if needed
            txt = "".join(part.decode() if isinstance(part, bytes) else str(part) for part in r.strings)
            print(f"  {txt}")
    except Exception as e:
        print("  (erreur TXT)", e)

if __name__ == "__main__":
    domain = "gmail.com"
    print_mx(domain)
    print_txt(domain)