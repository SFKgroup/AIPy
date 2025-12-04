from setuptools import setup, find_packages

def main():
    with open("README.md", "r",encoding="utf-8") as fh:
        long_description = fh.read()
    with open('requirements.txt',"r",encoding="utf-8") as f:
        required = f.read().splitlines()
    with open('LICENSE.txt',"r",encoding="utf-8") as f:
        license_text = f.read()


    setup(
        name='love-python', 
        version='0.1.2',
        packages=find_packages(),
        install_requires=required,
        author='FisherSteven',  
        author_email='steven05@163.com',
        description='AIpython is designed to effortlessly embed AI capabilities into Python, allowing users to solve problems through natural language descriptions and gradually transition to writing code.',
        long_description=long_description,
        long_description_content_type="text/markdown",
        license=license_text,
        classifiers=[
            'Programming Language :: Python :: 3',
            'Operating System :: OS Independent',
        ],
        python_requires='>=3.8',
    )
    
if __name__ == '__main__':
    main()