import unittest
from dotenv import load_dotenv

# Load environmental variables from .env file
load_dotenv()

def main():
    # Discover and run all the test files starting from the current directory.
    # This assumes all your test files have names starting with "test" or ending with "_test.py"
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='*_test.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == '__main__':
    main()
