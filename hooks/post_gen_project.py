import os, sys, re

# format README.md title
readme = os.getcwd() + '/README.md'
if (not os.path.exists(readme)):
    print('ERROR: file not found at %s' % (readme, ))
    sys.exit(1)

title_underliner = ''.center(len('{{cookiecutter.project_name}}'), '=')
f = open(readme, 'r')
content = f.read()
f.close()

f = open(readme, 'w')
f.write(re.sub(r'^=+$', title_underliner, content, 1, flags=re.M))
f.close()
# end format README.md title