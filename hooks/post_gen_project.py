import os, sys, re, shutil, filecmp

# fix template expansion after hook copy
# content: the duplicated hook content
# replacements: array of dictionaries of cookiecutter_key => key expanded
def fix_template_expansion(content, replacements):
    for replacement in replacements:
        for key, to_be_replaced in replacement.items():
            replacement = chr(123) + chr(123) + 'cookiecutter.' + key + chr(125) + chr(125)
            content = content.replace(to_be_replaced, replacement)
    return content

def get_file_content(filename):
    return open(filename, 'r').read()

def set_file_content(filename, content):
    return open(filename, 'w').write(content)

# format README.md title
readme = os.getcwd() + '/README.md'
if (os.path.exists(readme)):
    title_underliner = ''.center(len('{{cookiecutter.project_name}}'), '=')
    set_file_content(readme, re.sub(r'^=+$', title_underliner, get_file_content(readme), 1, flags=re.M))
# end format README.md title

# issue #3 - copy post hook to project directory
if (re.match(r'^cookiecutter\-', '{{cookiecutter.project_slug}}')):
    hooksdir = os.getcwd() + '/hooks'
    posthook = hooksdir + '/post_gen_project.py'
    source = os.path.realpath(__file__)
    replacements = [
        {'project_slug': '{{cookiecutter.project_slug}}'},

        # project_name must be set after project_slug to prevent side effects
        {'project_name': '{{cookiecutter.project_name}}'}
    ]

    if (not os.path.exists(hooksdir)):
        os.makedirs(hooksdir)
    shutil.copyfile(source, posthook)

    set_file_content(posthook, fix_template_expansion(get_file_content(posthook), replacements) + "\n")
# end issue #3
