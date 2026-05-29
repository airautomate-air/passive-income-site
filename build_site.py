#!/usr/bin/env python3
import os
import shutil
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape

def build_site():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(src_dir, 'dist')
    # Remove existing dist
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    # Create dist
    os.makedirs(dist_dir, exist_ok=True)

    # Setup Jinja2 environment
    # We'll treat the content directory as the template root for .j2 files.
    # Also allow a templates directory for base templates if needed.
    template_dirs = []
    content_dir = os.path.join(src_dir, 'content')
    if os.path.isdir(content_dir):
        template_dirs.append(content_dir)
    templates_dir = os.path.join(src_dir, 'templates')
    if os.path.isdir(templates_dir):
        template_dirs.append(templates_dir)
    # If no template dirs, just copy everything
    if not template_dirs:
        # fallback: copy all
        for item in os.listdir(src_dir):
            s = os.path.join(src_dir, item)
            d = os.path.join(dist_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, ignore=shutil.ignore_patterns('.git', '__pycache__', 'dist'))
            else:
                shutil.copy2(s, d)
        print(f"Site copied (no template support) to {dist_dir}")
        return

    env = Environment(
        loader=FileSystemLoader(template_dirs),
        autoescape=select_autoescape(['html', 'xml'])
    )

    # Walk through content directory
    for root, dirs, files in os.walk(content_dir):
        # Compute relative path from content_dir
        rel_path = os.path.relpath(root, content_dir)
        target_dir = os.path.join(dist_dir, rel_path) if rel_path != '.' else dist_dir
        os.makedirs(target_dir, exist_ok=True)
        for file in files:
            src_file = os.path.join(root, file)
            rel_file = os.path.relpath(src_file, src_dir)
            if file.endswith('.j2'):
                # Render template
                # Determine template name relative to template_dirs
                template_name = None
                for tdir in template_dirs:
                    candidate = os.path.relpath(src_file, tdir)
                    if not candidate.startswith('..') and os.path.isfile(os.path.join(tdir, candidate)):
                        template_name = candidate
                        break
                if template_name is None:
                    # fallback: treat as relative to content_dir
                    template_name = os.path.relpath(src_file, content_dir)
                try:
                    template = env.get_template(template_name)
                except Exception as e:
                    print(f"Error loading template {template_name}: {e}")
                    # copy as is (remove .j2)
                    dst_file = os.path.join(target_dir, file[:-3])  # remove .j2
                    shutil.copy2(src_file, dst_file)
                    continue
                output = template.render()
                # Output file without .j2 extension
                out_file = os.path.join(target_dir, file[:-3])  # remove .j2
                with open(out_file, 'w', encoding='utf-8') as f:
                    f.write(output)
            else:
                # Copy static file
                dst_file = os.path.join(target_dir, file)
                shutil.copy2(src_file, dst_file)

    # Also copy static assets at root (css, js, assets, etc.) if not already copied
    for item in ['css', 'js', 'assets']:
        src_item = os.path.join(src_dir, item)
        if os.path.isdir(src_item):
            dst_item = os.path.join(dist_dir, item)
            if os.path.exists(dst_item):
                shutil.rmtree(dst_item)
            shutil.copytree(src_item, dst_item)
    # Copy root-level files like index.html, etc. (excluding build_site.py, .gitignore)
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        if os.path.isfile(s) and item not in ['build_site.py', '.gitignore']:
            shutil.copy2(s, os.path.join(dist_dir, item))

    print(f"Site built to {dist_dir}")

if __name__ == '__main__':
    build_site()
