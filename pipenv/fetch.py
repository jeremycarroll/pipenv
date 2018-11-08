"""Interal CLI for fetching dependencies"""

from .resolver import ResolverCli

class FetchCli(ResolverCli):
    def run(self, sources):
        print("Not implemented")


if __name__ == "__main__":
    FetchCli().main()
