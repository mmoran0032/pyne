PyNE -- Python for Nuclear Experiments
======================================

PyNE is a package written during the end of my graduate career to support my
analysis of my thesis data in a purely Python environment. Instead of using a
suite such as `ROOT`_ (which has Python bindings), I wanted to avoid being
locked into using a package that I knew I would not be using after graduate
school. Additionally, the design and writing of this package allowed me to have
complete control over what was included and improve my software engineering.

The package is divided into (currently) three subpackages, divided by their
primary use and design requirements:

-   ``pyne`` provides basic datatypes
-   ``sap`` wraps up those datatypes in ways that are useful to minimize the
    amount of boilerplate code the scientist needs to write
-   ``tree`` collects target analysis codes together


PyNE
----

Files out of the ADC  are stored in ``.evt`` format, which must be processed
before it can be used. An additional DAQ system in use at Notre Dame saves its
files in the ``.Chn`` format. The processing for both of these file formats is
based on the `evt2root utility`_ by Karl Smith.

For most uses, the scientist will not need to interact with these objects
directly, aside from the top-level ``pyne.Data`` object.


SAP -- St. George Analysis Package
----------------------------------

St. George experiments are currently performed with a single 16-strip Si
detector, with full experiments also including two MCPs for timing signals.
Some of the routines could be adapted for other experiments, but that is beyond
the scope of this package.

-   ``display`` adds basic plotting functionality


TREE -- Target Response and Effect Environment
----------------------------------------------

For determining target effects, one of the more common utilities is `SRIM`_.
While this package doesn't avoid the use of this program, it does attempt to
make working with the files generate through SRIM easier for more complex
studies common in nuclear astrophysics for reaction studies which are more
difficult to do completely through SRIM.

For resonance scans especially, it is unfeasible to run SRIM to cover all
possible energies that are required. Instead, by utilizing a few a few energies
and locations within the target, you can get a pretty accurate view of the
target effects to simulate a full reaction.


.. _`evt2root utility`: https://github.com/ksmith0/evt2root
.. _`ROOT`: https://root.cern.ch/
.. _`SRIM`: http://www.srim.org/
