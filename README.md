# JBrowse Hub Creator
This Galaxy tool permits to prepare your files to be ready for JBrowse visualization.

## Features
1. Similar interface to Hub Archive Creator.
2. Convert tracks to GFF3 datatypes (e.g Blastxml => GFF3) in order to import feature data from the flat files
3. Group the tracks 
4. Set the color for each track
5. Set the label for each track
6. Create workflows within Galaxy to automatize pipeline analysis and get them ready to visualization inside JBrowse...in a few clicks!

At the moment, Supported datatypes are:
- Bam
- Bed 
  - Splice Junctions (BED 12+1)
  - Simple Repeats (BED 4+12)
- BigWig
- Gff3
- Gtf
- Blastxml
- BigPsl

## Installation:
1. You would need to add this tool into your Galaxy.
  1. (strongly preferred) **ToolShed Installation**: Tool is in [testtoolshed](https://testtoolshed.g2.bx.psu.edu/view/yating-l/jbrowse_hub/b7bf45272ab7)
  2. OR **Local Installation**: See https://wiki.galaxyproject.org/Admin/Tools/AddToolTutorial
2. The tool can be used with or without Conda (activate it in your galaxy.ini)
3. If installed without TS (by downloading on GitHub), you need to have all the binaries accessible within Galaxy.
   You can use the script [install_linux_binaries](util/install_linux_binaries) with a linux x86-64 (64bits)

## Future
See [TODO.md](todo.md) for more information

## Contribute

- Source Code: https://github.com/Yating-L/jbrowse_hub

## Support

If you are having issues, please let us know.

- For more information about how to use G-OnRamp:
    - [Wilson Leung](wleung@wustl.edu) - Product owner and developer
    - [Yating Liu](yliu41@wustl.edu) - Community manager and Developer

- For more information about the project vision, or for partneship:
    - [Elgin, Sarah](selgin@wustl.edu) - PI
    - [Jeremy Goecks](jgoecks@gwu.edu) - PI
    
## License

The project is licensed under the Academic Free License 3.0. See [LICENSE.txt](LICENSE.txt).
