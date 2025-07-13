from sqlalchemy import create_engine, exc
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.orm import sessionmaker
import os

MASIR_ASLI_BARNAMEH = os.path.dirname(os.path.abspath(__file__))
MASIR_AKS_PROFILE = os.path.join(MASIR_ASLI_BARNAMEH, "profile_images")
if not os.path.exists(MASIR_AKS_PROFILE):
    os.makedirs(MASIR_AKS_PROFILE)

Base = declarative_base()
engine = create_engine('sqlite:///Karbaran1.db')

class Karbaran(Base):
    __tablename__ = 'karbaran'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    phone: Mapped[int] = mapped_column(unique=True, nullable=False)
    bio: Mapped[str] = mapped_column(nullable=True)
    profile_image: Mapped[str] = mapped_column(nullable=False, default=os.path.join(MASIR_ASLI_BARNAMEH, "logo.jpg"))

Base.metadata.create_all(engine)

JalaseMahali = sessionmaker(bind=engine)

def ezafe_kardan_karbar(user_name, phone, password, bio=None, profile_image=None):
    jalase = JalaseMahali()
    if profile_image is None:
        profile_image = os.path.join(MASIR_ASLI_BARNAMEH, "logo.jpg")

    karbar = Karbaran(user_name=user_name, phone=phone, password=password, bio=bio, profile_image=profile_image)
    try:
        jalase.add(karbar)
        jalase.commit()
        return "Success"
    except exc.IntegrityError:
        jalase.rollback()
        return "Username or phone number already exists."
    finally:
        jalase.close()

def barresi_vorood(user_name, password):
    jalase = JalaseMahali()
    karbar = jalase.query(Karbaran).filter_by(user_name=user_name, password=password).first()
    jalase.close()
    return karbar is not None

def beroozresani_karbar(current_username, new_username=None, new_phone=None, new_password=None, new_bio=None, new_profile_image=None):
    jalase = JalaseMahali()
    karbar = jalase.query(Karbaran).filter_by(user_name=current_username).first()

    if not karbar:
        jalase.close()
        return "User doesn't exist."

    if new_username:
        karbar.user_name = new_username
    if new_phone:
        karbar.phone = new_phone
    if new_password:
        karbar.password = new_password
    if new_bio:
        karbar.bio = new_bio
    if new_profile_image:
        karbar.profile_image = new_profile_image

    try:
        jalase.commit()
        return "Success"
    except exc.IntegrityError:
        jalase.rollback()
        return "New username or phone number already exists."
    finally:
        jalase.close()

def peida_kardan_mokhatab(username, phone):
    jalase = JalaseMahali()
    try:
        phone_as_int = int(phone)
        mokhatab = jalase.query(Karbaran).filter_by(user_name=username, phone=phone_as_int).first()
        return mokhatab
    except (ValueError, TypeError):
        return None
    finally:
        jalase.close()

def namayesh_karbar(user_name):
    jalase = JalaseMahali()
    karbar = jalase.query(Karbaran).filter_by(user_name=user_name).first()
    jalase.close()
    return karbar