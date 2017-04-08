'''Registry of user interface widgets.

Format {"tool_key" : {"toolkit" : <function(obj, display, **kwargs)>}}

The ``tool_key` is defined by the "model function" to which the widget provides
and user interface. That function gets the widget function from this registry
and executes it passing the ``obj``, ``display`` and any extra keyword
arguments. When ``display`` is true, ``function`` displays the widget. If
``False`` it returns a dictionary with whatever is needed to display the
widgets externally (usually for testing or customisation purposes).

'''

import functools
import types

from hyperspy.misc.utils import isiterable


UI_REGISTRY = {}

TOOLKIT_REGISTRY = set()


def register_widget(toolkit, toolkey):
    """Decorator to register a UI widget.

    Parameters
    ----------
    f: function
        Function that returns or display the UI widget. The signature must
        include ``obj``, ``display`` and ``**kwargs``.
    toolkit: string
        The name of the widget toolkit e.g. ipywidgets
    toolkey: string
        The "key" of the tool for which the widget provides an interface. If
        the toolkey is not in the ``UI_REGISTRY`` dictionary a ``NameError``
        is raised.

    Returns
    -------
    widgets: dictionary or None
        Dictionary containing the widget objects if display is False, else None.

    """
    if not toolkey in UI_REGISTRY:
        raise NameError("%s is not a registered toolkey" % toolkey)
    TOOLKIT_REGISTRY.add(toolkit)

    def decorator(f):
        UI_REGISTRY[toolkey][toolkit] = f
        return f
    return decorator


def register_toolkey(toolkey):
    """Register a toolkey.

    Parameters
    ----------
    toolkey: string

    """
    if toolkey in UI_REGISTRY:
        raise NameError(
            "Another tool has been registered with the same name.")
    UI_REGISTRY[toolkey] = {}


def get_gui(self, toolkey, display=True, toolkit=None, **kwargs):
    if not TOOLKIT_REGISTRY:
        raise ImportError(
            "No toolkit installed. Install ipywidgets or traitsui to enable"
            "GUI elements"
        )
    from hyperspy.defaults_parser import preferences
    if isinstance(toolkit, str):
        toolkit = (toolkit,)
    if isiterable(toolkit):
        toolkits = set()
        for tk in toolkit:
            if tk in TOOLKIT_REGISTRY:
                toolkits.add(tk)
            else:
                raise ValueError(
                    "{} is not a registered toolkit.".format(tk)
                )
    elif toolkit is None:
        toolkits = []
        if preferences.General.enable_ipywidgets_gui:
            toolkits.append("ipywidgets")
        if preferences.General.enable_traitsui_gui:
            toolkits.append("traitsui")
        if not toolkits:
            return
    else:
        raise ValueError(
            "`toolkit` must be a string, an iterable of strings or None.")
    if toolkey not in UI_REGISTRY or not UI_REGISTRY[toolkey]:
        raise NotImplementedError(
            "There is no user interface registered for this feature."
            "Try installing ipywidgets or traitsui.")
    if not display:
        widgets = {}
    available_toolkits = set()
    used_toolkits = set()
    for toolkit, f in UI_REGISTRY[toolkey].items():
        if toolkit in toolkits:
            used_toolkits.add(toolkit)
            thisw = f(obj=self, display=display, **kwargs)
            if not display:
                widgets[toolkit] = thisw
        else:
            available_toolkits.add(toolkit)
    if not used_toolkits and available_toolkits:
        raise NotImplementedError(
            "The %s toolkits are not available for this functionality, "
            "try %s" % (toolkits, available_toolkits))
    if not display:
        return widgets


def get_partial_gui(toolkey):
    def pg(self, display=True, toolkit=None, **kwargs):
        return get_gui(self, toolkey=toolkey, display=display,
                       toolkit=toolkit, **kwargs)
    return pg

DISPLAY_DT = """display: bool
    If True, display the user interface widgets. If False, return the widgets
    container in a dictionary, usually for customisation or testing."""

TOOLKIT_DT = """toolkit: str, iterable of strings or None
    If None (default), all available widgets are displayed or returned. If
    string, only the widgets of the selected toolkit are displayed if available.
    If an interable of toolkit strings, the widgets of all listed toolkits are
    displayed or returned."""
GUI_DT = """Display or return interactive GUI element if available.

Parameters
----------
%s
%s

""" % (DISPLAY_DT, TOOLKIT_DT)


def add_gui_method(toolkey):
    def decorator(cls):
        register_toolkey(toolkey)
        # Not using functools.partialmethod because it is not possible to set
        # the docstring that way.
        setattr(cls, "gui", get_partial_gui(toolkey))
        setattr(cls.gui, "__doc__", GUI_DT)
        return cls
    return decorator


register_toolkey("interactive_range_selector")
register_toolkey("navigation_sliders")
register_toolkey("load")
