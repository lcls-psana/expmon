# expmon
A set of experiment monitoring tools.

## Documentation
- Sphinx generated documentation: https://lcls-psana.github.io/expmon/
<!--- - GitHub Pages: https://github.com/lcls-psana/expmon/wiki --->

## Quick start
### Create conda release
See for detail Psana Developer Documentation [3] 
```
cd <my-conda-release>
source conda_setup
```

### Clone package
**on pslogin:**
```
git clone https://github.com/lcls-psana/expmon.git
# or 
condarel --addpkg --name expmon --tag HEAD
```
### Build 
```
scons
```
Then run your application(s)

## References
- [1] https://lcls-psana.github.io/expmon/
- [2] https://github.com/lcls-psana/expmon/wiki
- [3] https://confluence.slac.stanford.edu/display/PSDMInternal/Psana+Developer+Documentation
- [4] https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet
