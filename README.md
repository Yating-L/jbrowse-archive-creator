# JBrowse Hub Creator
This Galaxy tool is used to prepare your files to be ready for JBrowse visualization.

## Features
1. Similar interface to Hub Archive Creator.
2. Convert tracks to GFF3 datatypes (e.g Blastxml => GFF3) in order to import feature data from the flat files
3. Group the tracks 
4. Set the color for each track
5. Set the label for each track
6. Support generating Tabix Indexed CanVasFeatures tracks
7. Create workflows within Galaxy to automatize pipeline analysis and get them ready to visualization inside JBrowse...in a few clicks!

At the moment, Supported datatypes are:
- BAM
- BED
  - Generic BED
  - Splice Junctions (BED 12+1)
  - Simple Repeats (BED 4+12)
  - BLAT alignment (BigPsl)
  - BLAST alignment (BED 12+12)
- BigWig
- GFF3
- GTF
- Blast XML output

## Installation:

**ToolShed Installation**: 

- The JBrowse Archive Creator tool is published at [ToolShed Repository](https://toolshed.g2.bx.psu.edu/view/yating-l/jbrowsearchivecreator)

- Refer to [Installing Tools into Galaxy](https://galaxyproject.org/admin/tools/add-tool-from-toolshed-tutorial) tutorial if you want to learn how to install a tool from ToolShed.
  
## Future
See [TODO.md](todo.md) for more information

## Contribute

- Source Code: https://github.com/goeckslab/jbrowse-archive-creator.git

## Support

If you are having issues, please let us know.

- For more information about how to use G-OnRamp:
    - [Wilson Leung](wleung@wustl.edu) - Product owner and developer
    - [Yating Liu](yliu41@wustl.edu) - Community manager and developer

- For more information about the project vision, or for partneship:
    - [Elgin, Sarah](selgin@wustl.edu) - PI
    - [Jeremy Goecks](jgoecks@gwu.edu) - PI
    
## License

The project is licensed under the Academic Free License 3.0. See [LICENSE.txt](LICENSE.txt).
