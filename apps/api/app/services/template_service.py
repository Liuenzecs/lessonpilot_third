from sqlmodel import Session, select

from app.models.template import Template, TemplateSection
from app.schemas.template import TemplateCreate, TemplateUpdate


def get_template(session: Session, template_id: str) -> Template | None:
    return session.get(Template, template_id)

def get_templates(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    subject: str | None = None,
    grade: str | None = None,
    is_public: bool | None = None,
) -> list[Template]:
    statement = select(Template)
    if subject:
        statement = statement.where(Template.subject == subject)
    if grade:
        statement = statement.where(Template.grade == grade)
    if is_public is not None:
        statement = statement.where(Template.is_public == is_public)
    statement = statement.offset(skip).limit(limit)
    return session.exec(statement).all()

def create_template(session: Session, template_in: TemplateCreate) -> Template:
    db_template = Template.model_validate(template_in, update={"sections": None})
    session.add(db_template)
    session.commit()
    session.refresh(db_template)

    if template_in.sections:
        for section in template_in.sections:
            db_section = TemplateSection(
                template_id=db_template.id,
                section_name=section.section_name,
                order=section.order,
                description=section.description,
                prompt_hints=section.prompt_hints,
                schema_constraints=section.schema_constraints,
            )
            session.add(db_section)
        session.commit()
    
    return db_template

def update_template(session: Session, db_template: Template, template_in: TemplateUpdate) -> Template:
    update_data = template_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template, field, value)
    
    session.add(db_template)
    session.commit()
    session.refresh(db_template)
    return db_template

def get_template_sections(session: Session, template_id: str) -> list[TemplateSection]:
    statement = (
        select(TemplateSection)
        .where(TemplateSection.template_id == template_id)
        .order_by(TemplateSection.order)
    )
    return session.exec(statement).all()
