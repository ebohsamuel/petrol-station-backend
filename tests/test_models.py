import pytest
from sqlalchemy import select
from app.models import Branch


# Test creating a branch
@pytest.mark.asyncio
async def test_create_branch(session):
    branch_data = Branch(name="Buvel", location="MM way")
    session.add(branch_data)
    await session.commit()
    await session.refresh(branch_data)

    result = await session.scalar(select(Branch).where(Branch.id == branch_data.id))
    assert result.name == "Buvel"
    assert result.location == "MM way"
