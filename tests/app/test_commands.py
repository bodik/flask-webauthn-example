"""fwe command tests"""

from fwe import db, commands


def test_dbinit_command(runner):
    """db init test"""

    result = runner.invoke(commands.dbinit_command)
    assert result.exit_code == 0


def test_dbremove_command(runner):
    """db remove test"""

    result = runner.invoke(commands.dbremove_command)
    assert result.exit_code == 0
    assert not db.engine.table_names()
