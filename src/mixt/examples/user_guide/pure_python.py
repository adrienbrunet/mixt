
# pylint: disable=missing-docstring,invalid-name,redefined-builtin,unused-argument,missing-param-doc,missing-type-doc
# flake8: noqa: D

"""The final "pure python" version of the todolist app presented in the user-guide.

To create the "pure-python" version:

    cp mixt.py pure-python.py
    black pure-python.py
    sed  -e 's/^# coding: mixt//' -e 's/"pure python"/"pure python"/' -i pure_python.py

"""

from typing import Callable, List, Union

from mixt import BaseContext, DefaultChoices, Element, Required, html


class TodoObject:
    """A simple object to host a todo entry, with just a text."""

    def __init__(self, text):
        self.text = text


def make_url(type: str) -> str:
    """Will compose a url based on the given type."""
    return f"/{type}/add"


class TodoForm(Element):
    """A Component to render the form used to add a toto entry."""

    class PropTypes:
        add_url: Union[Callable[[str], str], str] = make_url
        type: DefaultChoices = ["todo", "thing"]

    def render(self, context):

        if callable(self.add_url):
            add_url = self.add_url(self.type)
        else:
            add_url = self.add_url

        return html.Form(method="post", action=add_url)(
            html.Label()(html.Raw("New "), self.type, html.Raw(": ")),
            html.InputText(name="todo"),
            html.Button(type="submit")(html.Raw("Add")),
        )


class Todo(Element):
    """A component used to display a todo entry."""

    class PropTypes:
        todo: Required[TodoObject]

    def render(self, context):
        return html.Li()(self.todo.text)


class TodoList(Element):
    """ A component used to display a list of todo entries."""

    class PropTypes:
        todos: Required[List[TodoObject]]

    def render(self, context):
        return html.Ul()([Todo(todo=todo) for todo in self.todos])


class TodoApp(Element):
    """A component used to render the whole todo app."""

    class PropTypes:
        todos: Required[List[TodoObject]]
        type: DefaultChoices = ["todo", "thing"]

    def render(self, context):
        return html.Div()(
            html.H1()(html.Raw('The "'), self.type, html.Raw('" list')),
            TodoForm(type=self.type),
            TodoList(todos=self.todos),
        )


def thingify(WrappedComponent):
    """A "higher-order component" that force pass `type="thing"` to the wrapped component."""

    class HOC(Element):
        __display_name__ = f"thingify({WrappedComponent.__display_name__})"

        class PropTypes(WrappedComponent.PropTypes):
            __exclude__ = {"type"}

        def render(self, context):
            return WrappedComponent(type="thing", **self.props)(self.children())

    return HOC


def from_data_source(WrappedComponent, prop_name, get_source):
    """A "higher-order component" that fill the `prop_name` prop of the wrapped component with
    content coming from the `get_source` function."""

    class HOC(Element):
        __display_name__ = f"from_data_source({WrappedComponent.__display_name__})"

        class PropTypes(WrappedComponent.PropTypes):
            __exclude__ = {prop_name}

        def render(self, context):
            props = self.props.copy()
            props[prop_name] = get_source(props, context)
            return WrappedComponent(**props)(self.children())

    return HOC


class UserContext(BaseContext):
    """A context that will pass the authenticated user id down the whole components tree."""

    class PropTypes:
        authenticated_user_id: Required[int]


def get_todos(props, context):
    """A "data source" that will return some todo entries depending of the context user id."""
    if (
        not context.has_prop("authenticated_user_id")
        or not context.authenticated_user_id
    ):
        return []
    return {
        1: [TodoObject("1-1"), TodoObject("1-2")],
        2: [TodoObject("2-1"), TodoObject("2-2")],
    }[context.authenticated_user_id]


SourcedTodoApp = from_data_source(TodoApp, "todos", get_todos)
ThingApp = thingify(SourcedTodoApp)


def render_example():
    """Render the html for this example."""
    return str(UserContext(authenticated_user_id=1)(ThingApp()))


if __name__ == "__main__":
    print(render_example())